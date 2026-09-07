"""Orchestrate full and idempotent refresh imports from official Bundestag lists."""

from dataclasses import asdict, dataclass
from time import sleep
from urllib.parse import urlencode, urljoin

from selectolax.parser import HTMLParser
from sqlalchemy.orm import Session

from core.settings import Settings

from .fetcher import fetch_document
from .member_importer import import_biography
from .named_votes import import_named_vote
from .plenary_speeches import import_plenary_protocol


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
) -> ImportReport:
    """Import all discoverable current-term sources or refresh existing records."""
    report = ImportReport(mode="refresh" if refresh else "full", dry_run=dry_run)
    member_urls = discover_links(MEMBER_LIST_ENDPOINT, "/abgeordnete/biografien/", settings, limit)
    vote_urls = discover_links(NAMED_VOTE_LIST_ENDPOINT, ".xlsx", settings, limit)
    protocol_urls = discover_links(PROTOCOL_LIST_ENDPOINT, ".xml", settings, limit)
    report.discovered_members = len(member_urls)
    report.discovered_votes = len(vote_urls)
    report.discovered_protocols = len(protocol_urls)

    if dry_run:
        return report

    for url in member_urls:
        _import_one(report, "member", url, lambda: import_biography(session, url, settings.bundestag_electoral_term), settings)
    for url in vote_urls:
        _import_one(report, "vote", url, lambda: import_named_vote(session, url), settings)
    for url in protocol_urls:
        _import_one(report, "protocol", url, lambda: import_plenary_protocol(session, url), settings)
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
    try:
        importer()
    except Exception as error:
        report.failures.append(f"{source_type}: {url}: {error}")
    else:
        if source_type == "member":
            report.imported_members += 1
        elif source_type == "vote":
            report.imported_votes += 1
        else:
            report.imported_protocols += 1
    finally:
        sleep(1 / settings.crawler_requests_per_second)