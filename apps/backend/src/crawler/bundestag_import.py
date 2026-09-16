"""Orchestrate full and idempotent refresh imports from official Bundestag lists."""

import logging
import sys
from dataclasses import asdict, dataclass
from time import sleep
from urllib.parse import urlencode, urljoin

from selectolax.parser import HTMLParser
from sqlalchemy import select
from sqlalchemy.orm import Session

from core.settings import Settings

from .bundestag_biography import MDB_ID_PATTERN
from .fetcher import fetch_document
from .member_importer import import_biography
from .named_votes import import_named_vote
from .plenary_speeches import import_plenary_protocol

logger = logging.getLogger(__name__)

MEMBER_LIST_ENDPOINT = "https://www.bundestag.de/ajax/filterlist/de/abgeordnete/1040594-1040594"
NAMED_VOTE_LIST_ENDPOINT = "https://www.bundestag.de/ajax/filterlist/de/parlament/plenum/abstimmung/liste/462112-462112"
PROTOCOL_LIST_ENDPOINT = "https://www.bundestag.de/ajax/filterlist/de/services/opendata/1058442-1058442"


@dataclass
class ImportReport:
    mode: str
    dry_run: bool
    discovered_members: int = 0
    discovered_votes: int = 0
    discovered_protocols: int = 0
    imported_members: int = 0
    imported_votes: int = 0
    imported_protocols: int = 0
    skipped_members: int = 0
    skipped_votes: int = 0
    skipped_protocols: int = 0
    failures: list[str] | None = None

    def __post_init__(self) -> None:
        if self.failures is None:
            self.failures = []

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def run_bundestag_import(
    session: Session,
    settings: Settings,
    *,
    dry_run: bool = False,
    limit: int | None = None,
    refresh: bool = False,
    family: str | None = None,
) -> ImportReport:
    """Import all discoverable current-term sources or refresh existing records."""
    report = ImportReport(mode="refresh" if refresh else "full", dry_run=dry_run)
    member_urls = (
        discover_links(MEMBER_LIST_ENDPOINT, "/abgeordnete/biografien/", settings, limit)
        if family in (None, "members")
        else []
    )
    vote_urls = (
        discover_links(NAMED_VOTE_LIST_ENDPOINT, ".xlsx", settings, limit)
        if family in (None, "votes")
        else []
    )
    protocol_urls = (
        discover_links(PROTOCOL_LIST_ENDPOINT, ".xml", settings, limit)
        if family in (None, "protocols")
        else []
    )
    report.discovered_members = len(member_urls)
    report.discovered_votes = len(vote_urls)
    report.discovered_protocols = len(protocol_urls)

    if dry_run:
        return report

    # In refresh mode, pre-fetch existing source URLs from the database to skip unchanged documents
    existing_source_urls: set[str] = set()
    if refresh:
        from db.relational.models import SourceDocument

        all_candidate_urls = member_urls + vote_urls + protocol_urls
        if all_candidate_urls:
            existing_source_urls = set(
                session.scalars(
                    select(SourceDocument.requested_url).where(
                        SourceDocument.requested_url.in_(all_candidate_urls)
                    )
                ).all()
            )

    # 1. Members
    for idx, url in enumerate(member_urls, 1):
        if refresh and url in existing_source_urls:
            # Check if member still needs a portrait image
            from db.relational.models import BundestagMember, MemberImageCandidate

            match = MDB_ID_PATTERN.search(url)
            mdb_id = int(match.group(1)) if match else None
            needs_image = False
            if mdb_id:
                member_obj = session.scalar(select(BundestagMember).where(BundestagMember.mdb_id == mdb_id))
                if member_obj:
                    has_approved = session.scalar(
                        select(MemberImageCandidate.id).where(
                            MemberImageCandidate.member_id == member_obj.id,
                            MemberImageCandidate.status == "approved",
                        )
                    )
                    if not has_approved:
                        needs_image = True
            if not needs_image:
                report.skipped_members += 1
                continue

        sys.stderr.write(f"[{idx}/{len(member_urls)}] ")
        _import_one(
            report,
            "member",
            url,
            lambda u=url: import_biography(session, u, settings.bundestag_electoral_term, settings=settings),
            settings,
        )

    # 2. Named Votes (XLSX)
    for idx, url in enumerate(vote_urls, 1):
        if refresh and url in existing_source_urls:
            report.skipped_votes += 1
            continue
        sys.stderr.write(f"[{idx}/{len(vote_urls)}] ")
        _import_one(report, "vote", url, lambda u=url: import_named_vote(session, u), settings)

    # 3. Plenary Protocols (XML)
    for idx, url in enumerate(protocol_urls, 1):
        if refresh and url in existing_source_urls:
            report.skipped_protocols += 1
            continue
        sys.stderr.write(f"[{idx}/{len(protocol_urls)}] ")
        _import_one(report, "protocol", url, lambda u=url: import_plenary_protocol(session, u), settings)

    return report


def discover_links(endpoint: str, href_fragment: str, settings: Settings, limit: int | None = None) -> list[str]:
    """Collect unique official links from a paginated Bundestag filter-list endpoint."""
    offset = 0
    discovered: list[str] = []
    known_urls: set[str] = set()
    while limit is None or len(discovered) < limit:
        query = urlencode({"offset": offset})
        document = fetch_document(f"{endpoint}?{query}", settings)
        page_urls = _links_with_fragment(document.content.decode("utf-8"), href_fragment, base_url=endpoint)
        new_urls = [url for url in page_urls if url not in known_urls]
        for url in new_urls:
            known_urls.add(url)
            discovered.append(url)
            if limit is not None and len(discovered) == limit:
                return discovered

        headers_lower = {k.lower(): v for k, v in document.response_headers.items()}
        hits_count: int | None = None
        loaded_count: int | None = None

        if "hits-count" in headers_lower:
            try:
                hits_count = int(headers_lower["hits-count"])
            except ValueError:
                hits_count = None

        if "loaded-count" in headers_lower:
            try:
                loaded_count = int(headers_lower["loaded-count"])
            except ValueError:
                loaded_count = None

        step = loaded_count if loaded_count is not None else len(page_urls)
        if step <= 0:
            break

        if not new_urls and (hits_count is None or offset + step >= hits_count):
            break

        offset += step
        if hits_count is not None and offset >= hits_count:
            break

        sleep(1 / settings.crawler_requests_per_second)
    return discovered


def _links_with_fragment(html: str, href_fragment: str, base_url: str | None = None) -> list[str]:
    document = HTMLParser(html)
    urls: list[str] = []
    for link in document.css("a[href]"):
        href = link.attributes.get("href", "")
        if href_fragment in href:
            resolved = urljoin(base_url, href) if base_url else href
            urls.append(resolved)
    return urls


def _import_one(report: ImportReport, source_type: str, url: str, importer, settings: Settings) -> None:
    sys.stderr.write(f"-> [{source_type}] {url} ...\n")
    sys.stderr.flush()
    try:
        importer()
    except Exception as error:
        report.failures.append(f"{source_type}: {url}: {error}")
        sys.stderr.write(f"   [FEHLER] {error}\n")
        sys.stderr.flush()
    else:
        if source_type == "member":
            report.imported_members += 1
        elif source_type == "vote":
            report.imported_votes += 1
        else:
            report.imported_protocols += 1
    finally:
        sleep(1 / settings.crawler_requests_per_second)