"""Verified retrieval and ingestion of member profile portraits from Wikidata and Wikimedia Commons."""

import json
import logging
from datetime import UTC, datetime
from typing import Any
from urllib.parse import quote, urlencode

from selectolax.parser import HTMLParser
from sqlalchemy import select
from sqlalchemy.orm import Session

from core.settings import Settings
from db.relational.models import BundestagMember, MemberImageCandidate, SourceDocument

from .bundestag_biography import MemberBiography
from .fetcher import FetchedDocument, fetch_document

logger = logging.getLogger(__name__)

# Standard open licenses approved for unrestricted civic-tech use
APPROVED_LICENSE_KEYWORDS = (
    "cc0",
    "public domain",
    "pd",
    "cc-by",
    "cc by",
    "gfdl",
    "gnu free documentation license",
    "free art license",
)


def is_approved_open_license(license_name: str | None) -> bool:
    """Return True if license_name represents a recognized free/permissive license."""
    if not license_name:
        return False
    lower = license_name.lower().strip()
    # Explicitly reject non-commercial or no-derivatives variants if present
    if "nc" in lower or "nd" in lower:
        return False
    return any(keyword in lower for keyword in APPROVED_LICENSE_KEYWORDS)


def clean_html_text(raw_html: str | None) -> str | None:
    """Extract plain text from an HTML snippet or return stripped text."""
    if not raw_html:
        return None
    if "<" in raw_html and ">" in raw_html:
        parser = HTMLParser(raw_html)
        text = parser.text(separator=" ", strip=True)
        return text if text else None
    return raw_html.strip() if raw_html.strip() else None


def clean_media_url(url: str) -> str:
    """Strip unnecessary tracking/query parameters from a Wikimedia media URL."""
    return url.split("?")[0]


def get_or_create_source_document(
    session: Session,
    requested_url: str,
    document: FetchedDocument,
    publisher: str = "Wikimedia Commons",
) -> SourceDocument:
    """Idempotently persist source document metadata."""
    source = session.scalar(
        select(SourceDocument).where(
            SourceDocument.resolved_url == document.source.source_url,
            SourceDocument.content_sha256 == document.source.content_sha256,
        )
    )
    if source is not None:
        return source
    source = SourceDocument(
        publisher=publisher,
        requested_url=requested_url,
        resolved_url=document.source.source_url,
        retrieved_at=datetime.fromisoformat(document.source.retrieved_at),
        status_code=document.source.status_code,
        content_type=document.source.content_type,
        content_sha256=document.source.content_sha256,
        retrieval_tool="PolitiklarCrawler/0.1",
        snapshot_location=document.snapshot_location,
    )
    session.add(source)
    session.flush()
    return source


def resolve_wikidata_image(
    biography: MemberBiography,
    settings: Settings | None = None,
) -> tuple[str, str] | None:
    """Find the verified Wikidata QID and Commons image filename for an MdB.

    Crucially, to prevent name ambiguity/guessing, a candidate item is only accepted
    if it explicitly references the official MDB ID in P1713 (Bundestag biography URL)
    or P1186 (Bundestag member ID).
    """
    settings = settings or Settings()
    search_name = f"{biography.first_name or ''} {biography.last_name}".strip()
    if not search_name:
        return None

    search_query = urlencode(
        {
            "action": "wbsearchentities",
            "search": search_name,
            "language": "de",
            "format": "json",
        }
    )
    search_url = f"{settings.wikidata_api_url}?{search_query}"
    try:
        search_doc = fetch_document(search_url, settings)
        search_data = json.loads(search_doc.content.decode("utf-8"))
    except Exception as exc:
        logger.warning("Failed to search Wikidata entities for %s: %s", search_name, exc)
        return None

    search_results = search_data.get("search", [])
    if not search_results:
        return None

    entity_ids = [item["id"] for item in search_results[:10] if "id" in item]
    if not entity_ids:
        return None

    entities_query = urlencode(
        {
            "action": "wbgetentities",
            "ids": "|".join(entity_ids),
            "props": "claims",
            "format": "json",
        }
    )
    entities_url = f"{settings.wikidata_api_url}?{entities_query}"
    try:
        entities_doc = fetch_document(entities_url, settings)
        entities_data = json.loads(entities_doc.content.decode("utf-8"))
    except Exception as exc:
        logger.warning("Failed to fetch Wikidata claims for %s: %s", search_name, exc)
        return None

    entities = entities_data.get("entities", {})
    mdb_id_str = str(biography.mdb_id)

    for qid, entity in entities.items():
        claims = entity.get("claims", {})

        # P1713: Deutscher Bundestag biography URL
        p1713_claims = claims.get("P1713", [])
        p1713_values = [
            s.get("mainsnak", {}).get("datavalue", {}).get("value")
            for s in p1713_claims
            if isinstance(s, dict)
        ]

        # P1186: Bundestag person ID
        p1186_claims = claims.get("P1186", [])
        p1186_values = [
            s.get("mainsnak", {}).get("datavalue", {}).get("value")
            for s in p1186_claims
            if isinstance(s, dict)
        ]

        matched = False
        for val in p1713_values:
            if isinstance(val, str) and (f"-{mdb_id_str}" in val or f"/{mdb_id_str}" in val or mdb_id_str in val):
                matched = True
                break

        if not matched:
            for val in p1186_values:
                if str(val).strip() == mdb_id_str:
                    matched = True
                    break

        if matched:
            image_claims = claims.get("P18", [])
            if image_claims and isinstance(image_claims, list):
                val = image_claims[0].get("mainsnak", {}).get("datavalue", {}).get("value")
                if isinstance(val, str) and val.strip():
                    return qid, val.strip()

    return None


def fetch_commons_image_metadata(
    commons_filename: str,
    settings: Settings | None = None,
) -> tuple[dict[str, Any], FetchedDocument] | None:
    """Query Wikimedia Commons API for image file metadata."""
    settings = settings or Settings()
    if not commons_filename.startswith("File:"):
        full_title = f"File:{commons_filename}"
    else:
        full_title = commons_filename

    query = urlencode(
        {
            "action": "query",
            "titles": full_title,
            "prop": "imageinfo",
            "iiprop": "url|extmetadata|sha1",
            "format": "json",
        }
    )
    url = f"{settings.wikimedia_commons_api_url}?{query}"
    try:
        doc = fetch_document(url, settings)
        data = json.loads(doc.content.decode("utf-8"))
        pages = data.get("query", {}).get("pages", {})
        for page in pages.values():
            imageinfo = page.get("imageinfo")
            if imageinfo and isinstance(imageinfo, list) and len(imageinfo) > 0:
                info = imageinfo[0]
                return info, doc
    except Exception as exc:
        logger.warning("Failed to fetch Wikimedia Commons metadata for %s: %s", full_title, exc)
        return None

    return None


def fetch_and_import_member_image(
    session: Session,
    member: BundestagMember,
    biography: MemberBiography,
    settings: Settings | None = None,
) -> MemberImageCandidate | None:
    """Discover, retrieve metadata, and idempotently persist a portrait candidate."""
    settings = settings or Settings()

    # 1. Resolve Wikidata item and image filename
    resolution = resolve_wikidata_image(biography, settings)
    if resolution is None:
        logger.info("No verified Wikidata image found for MdB %s (%s %s)", biography.mdb_id, biography.first_name, biography.last_name)
        return None

    wikidata_qid, filename = resolution

    # 2. Fetch Commons metadata
    metadata_res = fetch_commons_image_metadata(filename, settings)
    if metadata_res is None:
        logger.warning("Could not fetch Commons imageinfo for %s (QID: %s)", filename, wikidata_qid)
        return None

    info, doc = metadata_res
    source_doc = get_or_create_source_document(session, doc.source.source_url, doc, publisher="Wikimedia Commons")

    media_url = clean_media_url(info.get("url", ""))
    commons_file_page_url = info.get("descriptionurl") or f"https://commons.wikimedia.org/wiki/File:{quote(filename)}"
    commons_sha1 = info.get("sha1")

    ext = info.get("extmetadata", {})
    license_name = ext.get("LicenseShortName", {}).get("value")
    license_url = ext.get("LicenseUrl", {}).get("value")
    raw_author = ext.get("Artist", {}).get("value")
    raw_credit = ext.get("Credit", {}).get("value")

    author = clean_html_text(raw_author)
    credit = clean_html_text(raw_credit)
    attribution_text = credit or (f"{author} / {license_name}" if author and license_name else author)

    license_approved = is_approved_open_license(license_name)

    # Check whether an approved image already exists for this member
    existing_approved = session.scalar(
        select(MemberImageCandidate.id).where(
            MemberImageCandidate.member_id == member.id,
            MemberImageCandidate.status == "approved",
        )
    )

    # If no approved image exists and license is approved, mark as approved
    if existing_approved is None and license_approved:
        status = "approved"
        reviewed_at = datetime.now(UTC)
        reviewed_by = "PolitiklarCrawler/WikimediaSync"
    else:
        status = "pending_review"
        reviewed_at = None
        reviewed_by = None

    # Check if candidate already exists for (member_id, commons_file_page_url)
    candidate = session.scalar(
        select(MemberImageCandidate).where(
            MemberImageCandidate.member_id == member.id,
            MemberImageCandidate.commons_file_page_url == commons_file_page_url,
        )
    )

    now = datetime.now(UTC)
    if candidate is None:
        candidate = MemberImageCandidate(
            member_id=member.id,
            source_document_id=source_doc.id,
            wikidata_qid=wikidata_qid,
            commons_file_page_url=commons_file_page_url,
            media_url=media_url,
            commons_filename=f"File:{filename}" if not filename.startswith("File:") else filename,
            commons_sha1=commons_sha1,
            author=author,
            attribution_text=attribution_text,
            license_name=license_name,
            license_url=license_url,
            license_approved=license_approved,
            status=status,
            reviewed_at=reviewed_at,
            reviewed_by=reviewed_by,
            retrieved_at=now,
        )
        session.add(candidate)
        session.flush()
    else:
        # Update metadata if needed
        candidate.source_document_id = source_doc.id
        candidate.wikidata_qid = wikidata_qid
        candidate.media_url = media_url
        candidate.author = author
        candidate.attribution_text = attribution_text
        candidate.license_name = license_name
        candidate.license_url = license_url
        candidate.license_approved = license_approved
        candidate.retrieved_at = now
        # If currently pending_review and can be approved (and no other approved image exists), promote
        if candidate.status == "pending_review" and existing_approved is None and license_approved:
            candidate.status = "approved"
            candidate.reviewed_at = reviewed_at
            candidate.reviewed_by = reviewed_by
        session.flush()

    return candidate
