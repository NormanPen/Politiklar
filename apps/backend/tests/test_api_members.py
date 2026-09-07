"""Tests for Bundestag members router."""

from datetime import date, datetime, timezone
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from db.relational.models import (
    BundestagMember,
    MemberAffiliation,
    MemberContactPoint,
    MemberExternalProfile,
    MemberImageCandidate,
    MemberMandate,
    MemberOffice,
    MemberProfileSnapshot,
    MemberTerm,
    SourceDocument,
)


def _seed_source_doc(db: Session) -> SourceDocument:
    doc = SourceDocument(
        id=uuid4(),
        publisher="Deutscher Bundestag",
        requested_url="https://www.bundestag.de/abgeordnete/biografien/A/example-1",
        resolved_url="https://www.bundestag.de/abgeordnete/biografien/A/example-1",
        retrieved_at=datetime.now(timezone.utc),
        status_code=200,
        content_type="text/html",
        content_sha256="test-sha-" + str(uuid4())[:8] + "0" * 46,
        retrieval_tool="politiklar-crawl/0.1",
    )
    db.add(doc)
    db.commit()
    return doc


def test_list_members_empty(client: TestClient) -> None:
    response = client.get("/api/v1/members")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["meta"]["total"] == 0
    assert data["meta"]["page"] == 1


def test_list_and_filter_members(client: TestClient, db_session: Session) -> None:
    doc = _seed_source_doc(db_session)

    # Member 1: SPD, term 20 and 21
    m1 = BundestagMember(mdb_id=1001)
    db_session.add(m1)
    db_session.commit()

    p1 = MemberProfileSnapshot(
        member_id=m1.id,
        source_document_id=doc.id,
        first_name="Max",
        last_name="Mustermann",
        parliamentary_group="SPD",
        occupation="Rechtsanwalt",
        content_sha256="m1-sha" + "0" * 58,
        is_current=True,
        observed_at=datetime.now(timezone.utc),
    )
    t1_20 = MemberTerm(member_id=m1.id, electoral_term=20, active=True, source_document_id=doc.id)
    t1_21 = MemberTerm(member_id=m1.id, electoral_term=21, active=True, source_document_id=doc.id)

    # Member 2: CDU/CSU, term 21
    m2 = BundestagMember(mdb_id=1002)
    db_session.add(m2)
    db_session.commit()

    p2 = MemberProfileSnapshot(
        member_id=m2.id,
        source_document_id=doc.id,
        first_name="Erika",
        last_name="Musterfrau",
        parliamentary_group="CDU/CSU",
        occupation="Ingenieurin",
        content_sha256="m2-sha" + "0" * 58,
        is_current=True,
        observed_at=datetime.now(timezone.utc),
    )
    t2_21 = MemberTerm(member_id=m2.id, electoral_term=21, active=True, source_document_id=doc.id)

    db_session.add_all([p1, t1_20, t1_21, p2, t2_21])
    db_session.commit()

    # Query all
    res_all = client.get("/api/v1/members")
    assert res_all.status_code == 200
    assert res_all.json()["meta"]["total"] == 2

    # Filter by group "SPD"
    res_spd = client.get("/api/v1/members?group=SPD")
    assert res_spd.status_code == 200
    assert res_spd.json()["meta"]["total"] == 1
    assert res_spd.json()["items"][0]["last_name"] == "Mustermann"

    # Filter by search "Erika"
    res_search = client.get("/api/v1/members?search=Erika")
    assert res_search.status_code == 200
    assert res_search.json()["meta"]["total"] == 1
    assert res_search.json()["items"][0]["mdb_id"] == 1002

    # Filter by term 20
    res_term20 = client.get("/api/v1/members?term=20")
    assert res_term20.status_code == 200
    assert res_term20.json()["meta"]["total"] == 1
    assert res_term20.json()["items"][0]["mdb_id"] == 1001


def test_get_member_by_mdb_id(client: TestClient, db_session: Session) -> None:
    doc = _seed_source_doc(db_session)

    m = BundestagMember(mdb_id=2001)
    db_session.add(m)
    db_session.commit()

    p = MemberProfileSnapshot(
        member_id=m.id,
        source_document_id=doc.id,
        first_name="Anna",
        last_name="Schmidt",
        parliamentary_group="Bündnis 90/Die Grünen",
        occupation="Biologin",
        content_sha256="m-sha" + "0" * 59,
        is_current=True,
        observed_at=datetime.now(timezone.utc),
    )
    term = MemberTerm(member_id=m.id, electoral_term=21, active=True, source_document_id=doc.id)
    office = MemberOffice(
        member_id=m.id,
        source_document_id=doc.id,
        office_type="bundestag",
        label="Platz der Republik 1",
        raw_address="Platz der Republik 1, 11011 Berlin",
        content_sha256="off-sha" + "0" * 57,
        observed_at=datetime.now(timezone.utc),
    )
    contact = MemberContactPoint(
        member_id=m.id,
        source_document_id=doc.id,
        contact_type="email",
        label="E-Mail",
        url="mailto:anna.schmidt@bundestag.de",
        content_sha256="cp-sha" + "0" * 58,
        observed_at=datetime.now(timezone.utc),
    )
    mandate = MemberMandate(
        member_id=m.id,
        source_document_id=doc.id,
        mandate_type="Landesliste",
        constituency_name="Hessen",
        start_date=date(2025, 2, 23),
        content_sha256="man-sha" + "0" * 57,
        observed_at=datetime.now(timezone.utc),
    )
    ext_profile = MemberExternalProfile(
        member_id=m.id,
        source_document_id=doc.id,
        platform="Website",
        raw_label="Persönliche Website",
        url="https://anna-schmidt.example.org",
        content_sha256="ep-sha" + "0" * 58,
        observed_at=datetime.now(timezone.utc),
    )
    affiliation = MemberAffiliation(
        member_id=m.id,
        source_document_id=doc.id,
        category="Mitgliedschaft",
        organization_name="BUND",
        role_name="Mitglied",
        content_sha256="aff-sha" + "0" * 57,
        observed_at=datetime.now(timezone.utc),
    )
    img = MemberImageCandidate(
        member_id=m.id,
        source_document_id=doc.id,
        commons_file_page_url="https://commons.wikimedia.org/wiki/File:Anna_Schmidt.jpg",
        media_url="https://upload.wikimedia.org/wikipedia/commons/anna_schmidt.jpg",
        commons_filename="File:Anna_Schmidt.jpg",
        author="FotoGraf",
        attribution_text="FotoGraf / CC-BY-SA-4.0",
        license_name="CC-BY-SA-4.0",
        license_url="https://creativecommons.org/licenses/by-sa/4.0/",
        license_approved=True,
        status="approved",
        retrieved_at=datetime.now(timezone.utc),
    )

    db_session.add_all([p, term, office, contact, mandate, ext_profile, affiliation, img])
    db_session.commit()

    response = client.get("/api/v1/members/2001")
    assert response.status_code == 200
    data = response.json()
    assert data["mdb_id"] == 2001
    assert data["first_name"] == "Anna"
    assert data["last_name"] == "Schmidt"
    assert data["parliamentary_group"] == "Bündnis 90/Die Grünen"
    assert data["image"]["media_url"] == "https://upload.wikimedia.org/wikipedia/commons/anna_schmidt.jpg"
    assert len(data["terms"]) == 1
    assert len(data["offices"]) == 1
    assert len(data["contact_points"]) == 1
    assert len(data["mandates"]) == 1
    assert len(data["external_profiles"]) == 1
    assert len(data["affiliations"]) == 1


def test_get_member_not_found(client: TestClient) -> None:
    response = client.get("/api/v1/members/999999")
    assert response.status_code == 404
    assert "999999 not found" in response.json()["detail"]
