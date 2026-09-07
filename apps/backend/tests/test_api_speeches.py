"""Tests for plenary speeches router."""

from datetime import datetime, timezone
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from db.relational.models import ParliamentarySpeech, SourceDocument


def _seed_source_doc(db: Session) -> SourceDocument:
    doc = SourceDocument(
        id=uuid4(),
        publisher="Deutscher Bundestag",
        requested_url="https://www.bundestag.de/resource/blob/protocol.xml",
        resolved_url="https://www.bundestag.de/resource/blob/protocol.xml",
        retrieved_at=datetime.now(timezone.utc),
        status_code=200,
        content_type="application/xml",
        content_sha256="speech-doc-sha-" + str(uuid4())[:8] + "0" * 41,
        retrieval_tool="politiklar-crawl/0.1",
    )
    db.add(doc)
    db.commit()
    return doc


def test_list_speeches_empty(client: TestClient) -> None:
    response = client.get("/api/v1/speeches")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["meta"]["total"] == 0


def test_list_and_filter_speeches(client: TestClient, db_session: Session) -> None:
    doc = _seed_source_doc(db_session)

    long_text = "Herr Präsident, meine sehr geehrten Damen und Herren! " + ("Wir debattieren heute einen Haushalt. " * 15)
    s1 = ParliamentarySpeech(
        id=uuid4(),
        protocol_source_document_id=doc.id,
        electoral_term=21,
        sitting_number=5,
        speech_locator="speech-1",
        speaker_source_id="11004500",
        first_name="Christian",
        last_name="Lindner",
        parliamentary_group="FDP",
        text=long_text,
        content_sha256="s1-sha" + "0" * 58,
        observed_at=datetime.now(timezone.utc),
    )
    s2 = ParliamentarySpeech(
        id=uuid4(),
        protocol_source_document_id=doc.id,
        electoral_term=21,
        sitting_number=5,
        speech_locator="speech-2",
        speaker_source_id="11004600",
        first_name="Rolf",
        last_name="Mützenich",
        parliamentary_group="SPD",
        text="Vielen Dank, Herr Präsident. Liebe Kolleginnen und Kollegen...",
        content_sha256="s2-sha" + "0" * 58,
        observed_at=datetime.now(timezone.utc),
    )
    db_session.add_all([s1, s2])
    db_session.commit()

    # List all
    res_all = client.get("/api/v1/speeches")
    assert res_all.status_code == 200
    data = res_all.json()
    assert data["meta"]["total"] == 2
    # Check truncation preview
    item1 = [it for it in data["items"] if it["last_name"] == "Lindner"][0]
    assert len(item1["text_preview"]) <= 260
    assert item1["text_preview"].endswith("...")

    # Filter by speaker
    res_speaker = client.get("/api/v1/speeches?speaker=Mützenich")
    assert res_speaker.status_code == 200
    assert res_speaker.json()["meta"]["total"] == 1
    assert res_speaker.json()["items"][0]["last_name"] == "Mützenich"

    # Search within text
    res_search = client.get("/api/v1/speeches?search=Haushalt")
    assert res_search.status_code == 200
    assert res_search.json()["meta"]["total"] == 1
    assert res_search.json()["items"][0]["last_name"] == "Lindner"

    # Get speech by ID
    res_detail = client.get(f"/api/v1/speeches/{s1.id}")
    assert res_detail.status_code == 200
    assert res_detail.json()["text"] == long_text


def test_get_speech_not_found(client: TestClient) -> None:
    non_existent = uuid4()
    response = client.get(f"/api/v1/speeches/{non_existent}")
    assert response.status_code == 404
