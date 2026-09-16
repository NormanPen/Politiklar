"""Tests for Wikidata and Wikimedia Commons member portrait retrieval and ingestion."""

import json
from datetime import UTC, datetime
from unittest.mock import patch
from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from crawler.bundestag_biography import MemberBiography
from crawler.fetcher import FetchedDocument, FetchedSource
from crawler.member_images import (
    clean_html_text,
    clean_media_url,
    fetch_and_import_member_image,
    fetch_commons_image_metadata,
    is_approved_open_license,
    resolve_wikidata_image,
)
from db.relational.models import BundestagMember, MemberImageCandidate, SourceDocument


def _make_mock_doc(url: str, json_data: dict) -> FetchedDocument:
    raw = json.dumps(json_data).encode("utf-8")
    return FetchedDocument(
        source=FetchedSource(
            source_url=url,
            retrieved_at=datetime.now(UTC).isoformat(),
            status_code=200,
            content_type="application/json",
            content_sha256="sha256-" + url[:20].replace("/", "_"),
            title=None,
        ),
        content=raw,
        response_headers={"content-type": "application/json"},
        snapshot_location=None,
    )


def test_is_approved_open_license() -> None:
    assert is_approved_open_license("CC BY-SA 4.0") is True
    assert is_approved_open_license("CC-BY-SA-3.0") is True
    assert is_approved_open_license("CC BY 2.0") is True
    assert is_approved_open_license("CC0") is True
    assert is_approved_open_license("Public domain") is True
    assert is_approved_open_license("GFDL") is True
    assert is_approved_open_license("Free Art License") is True

    # Disallowed non-commercial or no-derivatives variants
    assert is_approved_open_license("CC BY-NC 4.0") is False
    assert is_approved_open_license("CC BY-ND 3.0") is False
    assert is_approved_open_license("CC-BY-NC-SA 2.0") is False

    # Disallowed/unknown licenses
    assert is_approved_open_license(None) is False
    assert is_approved_open_license("") is False
    assert is_approved_open_license("All Rights Reserved") is False


def test_clean_html_text() -> None:
    assert clean_html_text(None) is None
    assert clean_html_text("") is None
    assert clean_html_text("Photothek") == "Photothek"
    assert clean_html_text('<a href="https://example.org">Photothek</a>') == "Photothek"
    assert clean_html_text("<span>Uwe Steinert</span> / <b>CC-BY</b>") == "Uwe Steinert / CC-BY"


def test_clean_media_url() -> None:
    raw = "https://upload.wikimedia.org/wikipedia/commons/2/2e/Abdi_Sanae.jpg?utm_source=commons&utm_content=orig"
    assert clean_media_url(raw) == "https://upload.wikimedia.org/wikipedia/commons/2/2e/Abdi_Sanae.jpg"
    assert clean_media_url("https://upload.wikimedia.org/pic.jpg") == "https://upload.wikimedia.org/pic.jpg"


def test_resolve_wikidata_image_verified_via_p1713() -> None:
    bio = MemberBiography(
        mdb_id=1043330,
        first_name="Sanae",
        last_name="Abdi",
        name_prefix=None,
        occupation=None,
        parliamentary_group="SPD",
        mandate_start=None,
        offices=(),
        contact_points=(),
        mandates=(),
        external_profiles=(),
        affiliations=(),
        content_sha256="test-sha",
    )

    search_payload = {
        "search": [{"id": "Q108733090", "label": "Sanae Abdi"}]
    }
    entities_payload = {
        "entities": {
            "Q108733090": {
                "claims": {
                    "P1713": [
                        {"mainsnak": {"datavalue": {"value": "https://www.bundestag.de/abgeordnete/biografien/A/abdi_sanae-1043330"}}}
                    ],
                    "P18": [
                        {"mainsnak": {"datavalue": {"value": "Abdi Sanae.jpg"}}}
                    ],
                }
            }
        }
    }

    def mock_fetch(url: str, settings=None):
        if "wbsearchentities" in url:
            return _make_mock_doc(url, search_payload)
        if "wbgetentities" in url:
            return _make_mock_doc(url, entities_payload)
        raise AssertionError(f"Unexpected URL: {url}")

    with patch("crawler.member_images.fetch_document", side_effect=mock_fetch):
        res = resolve_wikidata_image(bio)
        assert res == ("Q108733090", "Abdi Sanae.jpg")


def test_resolve_wikidata_image_rejects_unverified_candidate() -> None:
    """Proves no name guessing: an entity with matching name but wrong/missing MdB ID is rejected."""
    bio = MemberBiography(
        mdb_id=9999999,
        first_name="Sanae",
        last_name="Abdi",
        name_prefix=None,
        occupation=None,
        parliamentary_group="SPD",
        mandate_start=None,
        offices=(),
        contact_points=(),
        mandates=(),
        external_profiles=(),
        affiliations=(),
        content_sha256="test-sha",
    )

    search_payload = {
        "search": [{"id": "Q108733090", "label": "Sanae Abdi"}]
    }
    # Entity claims point to MdB 1043330, but bio has 9999999
    entities_payload = {
        "entities": {
            "Q108733090": {
                "claims": {
                    "P1713": [
                        {"mainsnak": {"datavalue": {"value": "https://www.bundestag.de/abgeordnete/biografien/A/abdi_sanae-1043330"}}}
                    ],
                    "P18": [
                        {"mainsnak": {"datavalue": {"value": "Abdi Sanae.jpg"}}}
                    ],
                }
            }
        }
    }

    def mock_fetch(url: str, settings=None):
        if "wbsearchentities" in url:
            return _make_mock_doc(url, search_payload)
        if "wbgetentities" in url:
            return _make_mock_doc(url, entities_payload)
        raise AssertionError(f"Unexpected URL: {url}")

    with patch("crawler.member_images.fetch_document", side_effect=mock_fetch):
        res = resolve_wikidata_image(bio)
        assert res is None


def test_fetch_commons_image_metadata() -> None:
    commons_payload = {
        "query": {
            "pages": {
                "12345": {
                    "title": "File:Abdi Sanae.jpg",
                    "imageinfo": [
                        {
                            "url": "https://upload.wikimedia.org/wikipedia/commons/2/2e/Abdi_Sanae.jpg?utm=1",
                            "descriptionurl": "https://commons.wikimedia.org/wiki/File:Abdi_Sanae.jpg",
                            "sha1": "00479566038ec7706e130af0dc8190bb0fb70799",
                            "extmetadata": {
                                "Artist": {"value": '<a href="https://example.com">Photothek</a>'},
                                "Credit": {"value": "SPD Fraktion"},
                                "LicenseShortName": {"value": "CC BY-SA 4.0"},
                                "LicenseUrl": {"value": "https://creativecommons.org/licenses/by-sa/4.0"},
                            },
                        }
                    ],
                }
            }
        }
    }

    with patch("crawler.member_images.fetch_document", return_value=_make_mock_doc("https://commons.wikimedia.org", commons_payload)):
        res = fetch_commons_image_metadata("Abdi Sanae.jpg")
        assert res is not None
        info, _ = res
        assert info["sha1"] == "00479566038ec7706e130af0dc8190bb0fb70799"
        assert info["extmetadata"]["LicenseShortName"]["value"] == "CC BY-SA 4.0"


def test_fetch_and_import_member_image_lifecycle(db_session: Session) -> None:
    # 1. Setup member
    member = BundestagMember(id=uuid4(), mdb_id=1043330)
    db_session.add(member)
    db_session.commit()

    bio = MemberBiography(
        mdb_id=1043330,
        first_name="Sanae",
        last_name="Abdi",
        name_prefix=None,
        occupation=None,
        parliamentary_group="SPD",
        mandate_start=None,
        offices=(),
        contact_points=(),
        mandates=(),
        external_profiles=(),
        affiliations=(),
        content_sha256="test-sha",
    )

    fake_doc = _make_mock_doc("https://commons.wikimedia.org/w/api.php?test", {})
    commons_info = {
        "url": "https://upload.wikimedia.org/wikipedia/commons/2/2e/Abdi_Sanae.jpg?utm_source=commons",
        "descriptionurl": "https://commons.wikimedia.org/wiki/File:Abdi_Sanae.jpg",
        "sha1": "00479566038ec7706e130af0dc8190bb0fb70799",
        "extmetadata": {
            "Artist": {"value": "Photothek"},
            "Credit": {"value": "SPD Fraktion / Photothek"},
            "LicenseShortName": {"value": "CC BY-SA 4.0"},
            "LicenseUrl": {"value": "https://creativecommons.org/licenses/by-sa/4.0"},
        },
    }

    with patch("crawler.member_images.resolve_wikidata_image", return_value=("Q108733090", "Abdi Sanae.jpg")), \
         patch("crawler.member_images.fetch_commons_image_metadata", return_value=(commons_info, fake_doc)):

        candidate = fetch_and_import_member_image(db_session, member, bio)
        db_session.commit()

        assert candidate is not None
        assert candidate.member_id == member.id
        assert candidate.wikidata_qid == "Q108733090"
        assert candidate.media_url == "https://upload.wikimedia.org/wikipedia/commons/2/2e/Abdi_Sanae.jpg"
        assert candidate.license_name == "CC BY-SA 4.0"
        assert candidate.license_approved is True
        assert candidate.status == "approved"
        assert candidate.author == "Photothek"
        assert candidate.attribution_text == "SPD Fraktion / Photothek"

        # Verify source document linkage
        source = db_session.scalar(select(SourceDocument).where(SourceDocument.id == candidate.source_document_id))
        assert source is not None
        assert source.publisher == "Wikimedia Commons"

        # Test idempotency: second import run updates without duplicating
        candidate2 = fetch_and_import_member_image(db_session, member, bio)
        db_session.commit()
        assert candidate2.id == candidate.id

        total_candidates = db_session.scalars(
            select(MemberImageCandidate).where(MemberImageCandidate.member_id == member.id)
        ).all()
        assert len(total_candidates) == 1
