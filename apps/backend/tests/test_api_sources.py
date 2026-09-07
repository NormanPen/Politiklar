"""Tests for source document provenance endpoints."""

from datetime import datetime, timezone
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from db.relational.models import SourceDocument


def test_get_source_document_by_id(client: TestClient, db_session: Session) -> None:
    doc_id = uuid4()
    doc = SourceDocument(
        id=doc_id,
        publisher="Deutscher Bundestag",
        requested_url="https://www.bundestag.de/abgeordnete/biografien/A/example-1",
        resolved_url="https://www.bundestag.de/abgeordnete/biografien/A/example-1",
        retrieved_at=datetime.now(timezone.utc),
        status_code=200,
        content_type="text/html",
        content_sha256="abc123sha256" + "0" * 52,
        retrieval_tool="politiklar-crawl/0.1",
        snapshot_location="var/source-archive/ab/test",
    )
    db_session.add(doc)
    db_session.commit()

    response = client.get(f"/api/v1/sources/{doc_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(doc_id)
    assert data["publisher"] == "Deutscher Bundestag"
    assert data["content_sha256"] == "abc123sha256" + "0" * 52


def test_get_source_document_not_found(client: TestClient) -> None:
    non_existent = uuid4()
    response = client.get(f"/api/v1/sources/{non_existent}")
    assert response.status_code == 404
    assert f"'{non_existent}' not found" in response.json()["detail"]


def test_get_source_document_by_sha256(client: TestClient, db_session: Session) -> None:
    sha = "fedcba9876543210" + "1" * 48
    doc = SourceDocument(
        publisher="Deutscher Bundestag",
        requested_url="https://www.bundestag.de/resource/blob/vote.xlsx",
        resolved_url="https://www.bundestag.de/resource/blob/vote.xlsx",
        retrieved_at=datetime.now(timezone.utc),
        status_code=200,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        content_sha256=sha,
        retrieval_tool="politiklar-crawl/0.1",
    )
    db_session.add(doc)
    db_session.commit()

    response = client.get(f"/api/v1/sources/by-sha256/{sha}")
    assert response.status_code == 200
    data = response.json()
    assert data["content_sha256"] == sha


def test_get_source_document_by_sha256_not_found(client: TestClient) -> None:
    response = client.get("/api/v1/sources/by-sha256/nonexistent-hash")
    assert response.status_code == 404
