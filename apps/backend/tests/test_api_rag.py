"""Integration tests for RAG API endpoints."""

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from api.dependencies import get_settings
from core.settings import Settings
from rag.prompts import INSUFFICIENT_EVIDENCE_MESSAGE


def test_rag_ask_returns_503_when_api_key_missing(client: TestClient, monkeypatch) -> None:
    test_settings = Settings(gemini_api_key="")
    client.app.dependency_overrides[get_settings] = lambda: test_settings

    response = client.post("/api/v1/rag/ask", json={"question": "Was sagte Abgeordnete Mustermann?"})
    assert response.status_code == 503
    assert "Gemini API is not configured" in response.json()["detail"]


def test_rag_ask_validation_error_on_short_question(client: TestClient) -> None:
    response = client.post("/api/v1/rag/ask", json={"question": "a"})
    assert response.status_code == 422


def test_rag_ask_returns_insufficient_evidence_when_no_chunks(client: TestClient) -> None:
    test_settings = Settings(gemini_api_key="mock_key")
    client.app.dependency_overrides[get_settings] = lambda: test_settings

    # Mock query embedding and search to test endpoint logic without PostgreSQL pgvector in SQLite test
    with (
        patch("rag.service.RagService.get_query_embedding", return_value=[0.0] * 768),
        patch("rag.service.RagService.search_similar_chunks", return_value=[]),
    ):
        response = client.post(
            "/api/v1/rag/ask",
            json={"question": "Welche Position vertritt Fraktion X zur Steuerreform?"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_sufficient_evidence"] is False
        assert data["answer"] == INSUFFICIENT_EVIDENCE_MESSAGE
        assert data["citations"] == []
        assert data["chunks"] == []


def test_rag_search_returns_chunks(client: TestClient) -> None:
    from uuid import uuid4
    from rag.service import RetrievedChunk

    test_settings = Settings(gemini_api_key="mock_key")
    client.app.dependency_overrides[get_settings] = lambda: test_settings

    mock_chunk = RetrievedChunk(
        chunk_id=uuid4(),
        source_document_id=uuid4(),
        speech_id=uuid4(),
        chunk_index=0,
        content="Die Abgeordnete betonte die Notwendigkeit von Investitionen in Bildung.",
        metadata={"speech_locator": "Plenarprotokoll 21/10", "speaker_name": "Erika Mustermann"},
        similarity_score=0.88,
    )

    with (
        patch("rag.service.RagService.get_query_embedding", return_value=[0.0] * 768),
        patch("rag.service.RagService.search_similar_chunks", return_value=[mock_chunk]),
    ):
        response = client.post("/api/v1/rag/search", json={"question": "Bildungsinvestitionen"})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["content"] == "Die Abgeordnete betonte die Notwendigkeit von Investitionen in Bildung."
        assert data[0]["similarity_score"] == 0.88


def test_rag_ask_generates_grounded_answer(client: TestClient) -> None:
    from uuid import uuid4
    from rag.service import RetrievedChunk

    test_settings = Settings(gemini_api_key="mock_key")
    client.app.dependency_overrides[get_settings] = lambda: test_settings

    source_id = uuid4()
    mock_chunk = RetrievedChunk(
        chunk_id=uuid4(),
        source_document_id=source_id,
        speech_id=uuid4(),
        chunk_index=0,
        content="Die Abgeordnete betonte die Notwendigkeit von Investitionen in Bildung.",
        metadata={"speech_locator": "Plenarprotokoll 21/10, S. 120", "speaker_name": "Erika Mustermann"},
        similarity_score=0.91,
    )

    mock_llm_response = MagicMock()
    mock_llm_response.content = f"Abgeordnete Mustermann forderte Bildungsinvestitionen [Quelle: {source_id}, Plenarprotokoll 21/10, S. 120]."

    with (
        patch("rag.service.RagService.get_query_embedding", return_value=[0.0] * 768),
        patch("rag.service.RagService.search_similar_chunks", return_value=[mock_chunk]),
        patch("rag.service.ChatGoogleGenerativeAI.invoke", return_value=mock_llm_response),
    ):
        response = client.post(
            "/api/v1/rag/ask",
            json={"question": "Welche Position vertritt Frau Mustermann zu Bildung?"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_sufficient_evidence"] is True
        assert "Abgeordnete Mustermann forderte" in data["answer"]
        assert len(data["citations"]) == 1
        assert data["citations"][0]["speaker"] == "Erika Mustermann"
        assert len(data["chunks"]) == 1

