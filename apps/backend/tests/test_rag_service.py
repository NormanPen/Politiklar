"""Unit tests for RagService and Gemini embeddings wiring."""

from unittest.mock import MagicMock, patch

from core.settings import Settings
from rag.service import RagService


def test_rag_service_get_query_embedding_uses_configured_dimension() -> None:
    settings = Settings(
        gemini_api_key="mock_key",
        gemini_embedding_dimension=768,
    )
    rag_service = RagService(settings)

    mock_client = MagicMock()
    mock_client.embed_query.return_value = [0.1] * 768

    with patch("rag.service.get_embeddings_client", return_value=mock_client):
        result = rag_service.get_query_embedding("Test-Anfrage")

    assert result == [0.1] * 768
    mock_client.embed_query.assert_called_once_with(
        "Test-Anfrage",
        output_dimensionality=768,
    )


def test_rag_service_get_documents_embeddings_uses_configured_dimension() -> None:
    settings = Settings(
        gemini_api_key="mock_key",
        gemini_embedding_dimension=768,
    )
    rag_service = RagService(settings)

    mock_client = MagicMock()
    mock_client.embed_documents.return_value = [[0.1] * 768, [0.2] * 768]

    with patch("rag.service.get_embeddings_client", return_value=mock_client):
        result = rag_service.get_documents_embeddings(["Dokument 1", "Dokument 2"])

    assert len(result) == 2
    mock_client.embed_documents.assert_called_once_with(
        ["Dokument 1", "Dokument 2"],
        output_dimensionality=768,
    )
