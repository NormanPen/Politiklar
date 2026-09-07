"""Tests for named votes router."""

from datetime import datetime, timezone
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from db.relational.models import NamedVote, NamedVoteRow, SourceDocument


def _seed_source_doc(db: Session) -> SourceDocument:
    doc = SourceDocument(
        id=uuid4(),
        publisher="Deutscher Bundestag",
        requested_url="https://www.bundestag.de/resource/blob/vote.xlsx",
        resolved_url="https://www.bundestag.de/resource/blob/vote.xlsx",
        retrieved_at=datetime.now(timezone.utc),
        status_code=200,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        content_sha256="vote-doc-sha-" + str(uuid4())[:8] + "0" * 43,
        retrieval_tool="politiklar-crawl/0.1",
    )
    db.add(doc)
    db.commit()
    return doc


def test_list_votes_empty(client: TestClient) -> None:
    response = client.get("/api/v1/votes")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["meta"]["total"] == 0


def test_list_and_get_vote_details(client: TestClient, db_session: Session) -> None:
    doc = _seed_source_doc(db_session)

    vote = NamedVote(
        id=uuid4(),
        source_document_id=doc.id,
        electoral_term=21,
        sitting_number=4,
        vote_number=1,
        title="Gesetzentwurf zur Haushaltsstabilisierung",
        content_sha256="vote-sha" + "0" * 56,
        retrieved_at=datetime.now(timezone.utc),
    )
    db_session.add(vote)
    db_session.commit()

    # Add 4 rows with distinct outcomes
    rows = [
        NamedVoteRow(
            named_vote_id=vote.id,
            source_document_id=doc.id,
            parliamentary_group="SPD",
            first_name="Max",
            last_name="Mustermann",
            raw_outcome="ja",
            outcome="yes",
            content_sha256="row1-sha" + "0" * 56,
            observed_at=datetime.now(timezone.utc),
        ),
        NamedVoteRow(
            named_vote_id=vote.id,
            source_document_id=doc.id,
            parliamentary_group="CDU/CSU",
            first_name="Erika",
            last_name="Musterfrau",
            raw_outcome="nein",
            outcome="no",
            content_sha256="row2-sha" + "0" * 56,
            observed_at=datetime.now(timezone.utc),
        ),
        NamedVoteRow(
            named_vote_id=vote.id,
            source_document_id=doc.id,
            parliamentary_group="FDP",
            first_name="Christian",
            last_name="Beispiel",
            raw_outcome="Enthaltung",
            outcome="abstained",
            content_sha256="row3-sha" + "0" * 56,
            observed_at=datetime.now(timezone.utc),
        ),
        NamedVoteRow(
            named_vote_id=vote.id,
            source_document_id=doc.id,
            parliamentary_group="AfD",
            first_name="Hans",
            last_name="Test",
            raw_outcome="nichtabgegeben",
            outcome="not_voted",
            content_sha256="row4-sha" + "0" * 56,
            observed_at=datetime.now(timezone.utc),
        ),
    ]
    db_session.add_all(rows)
    db_session.commit()

    # Test listing votes
    list_res = client.get("/api/v1/votes?term=21")
    assert list_res.status_code == 200
    list_data = list_res.json()
    assert list_data["meta"]["total"] == 1
    summary = list_data["items"][0]
    assert summary["title"] == "Gesetzentwurf zur Haushaltsstabilisierung"
    assert summary["breakdown"]["total"] == 4
    assert summary["breakdown"]["yes"] == 1
    assert summary["breakdown"]["no"] == 1
    assert summary["breakdown"]["abstained"] == 1
    assert summary["breakdown"]["not_voted"] == 1

    # Test vote detail
    detail_res = client.get(f"/api/v1/votes/{vote.id}")
    assert detail_res.status_code == 200
    detail_data = detail_res.json()
    assert detail_data["id"] == str(vote.id)
    assert len(detail_data["rows"]) == 4
    assert detail_data["breakdown"]["yes"] == 1


def test_get_vote_not_found(client: TestClient) -> None:
    non_existent = uuid4()
    response = client.get(f"/api/v1/votes/{non_existent}")
    assert response.status_code == 404
