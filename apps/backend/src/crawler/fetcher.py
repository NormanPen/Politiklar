"""HTTP retrieval with metadata needed to trace a source document."""

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from time import sleep

import httpx
from selectolax.parser import HTMLParser

from core.settings import Settings


@dataclass(frozen=True)
class FetchedSource:
    source_url: str
    retrieved_at: str
    status_code: int
    content_type: str
    content_sha256: str
    title: str | None

    def to_dict(self) -> dict[str, str | int | None]:
        return asdict(self)


@dataclass(frozen=True)
class FetchedDocument:
    source: FetchedSource
    content: bytes
    response_headers: dict[str, str]
    snapshot_location: str | None


def fetch_document(url: str, settings: Settings | None = None) -> FetchedDocument:
    """Retrieve a document and its immutable source metadata."""
    settings = settings or Settings()
    retrieved_at = datetime.now(UTC).isoformat()

    with httpx.Client(
        follow_redirects=True,
        headers={"User-Agent": settings.crawler_user_agent},
        timeout=settings.crawler_request_timeout_seconds,
    ) as client:
        response = _get_with_retry(client, url, settings)

    if len(response.content) > settings.crawler_max_response_bytes:
        raise ValueError(f"Response exceeds configured size limit of {settings.crawler_max_response_bytes} bytes.")

    content_type = response.headers.get("content-type", "")
    document = HTMLParser(response.text) if "html" in content_type else None
    title_node = document.css_first("title") if document else None
    content_hash = sha256(response.content).hexdigest()
    snapshot_location = _archive_content(response.content, content_hash, settings.crawler_source_archive_path)

    return FetchedDocument(
        source=FetchedSource(
            source_url=str(response.url),
            retrieved_at=retrieved_at,
            status_code=response.status_code,
            content_type=content_type,
            content_sha256=content_hash,
            title=title_node.text(strip=True) if title_node else None,
        ),
        content=response.content,
        response_headers=dict(response.headers),
        snapshot_location=str(snapshot_location),
    )


def fetch_source(url: str) -> FetchedSource:
    """Retrieve a source document and return its provenance metadata."""
    return fetch_document(url).source


def _get_with_retry(client: httpx.Client, url: str, settings: Settings) -> httpx.Response:
    for attempt in range(settings.crawler_max_retries + 1):
        try:
            response = client.get(url)
            response.raise_for_status()
            return response
        except (httpx.NetworkError, httpx.TimeoutException, httpx.HTTPStatusError):
            if attempt == settings.crawler_max_retries:
                raise
            sleep(1 / settings.crawler_requests_per_second * (2**attempt))
    raise RuntimeError("Unreachable retry state.")


def _archive_content(content: bytes, content_hash: str, archive_root: Path) -> Path:
    snapshot_location = archive_root / content_hash[:2] / content_hash
    snapshot_location.parent.mkdir(parents=True, exist_ok=True)
    if not snapshot_location.exists():
        snapshot_location.write_bytes(content)
    return snapshot_location