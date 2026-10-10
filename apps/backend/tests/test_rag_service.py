"""Unit tests for modular AI providers, GeminiProvider, and RagService."""

from unittest.mock import MagicMock, patch
import pytest

from core.settings import Settings
from rag.providers import (
    AIProvider,
    GeminiProvider,
    get_ai_provider,
    register_ai_provider,
)
from rag.service import RagService


def test_gemini_provider_is_configured() -> None:
    unconfigured = GeminiProvider(Settings(gemini_api_key=""))
    assert unconfigured.is_configured is False

    configured = GeminiProvider(Settings(gemini_api_key="test_key_123"))
    assert configured.is_configured is True
    assert configured.name == "gemini"


def test_gemini_provider_embed_query_uses_configured_dimension() -> None:
    settings = Settings(
        gemini_api_key="mock_key",
        gemini_embedding_dimension=768,
    )
    provider = GeminiProvider(settings)

    mock_client = MagicMock()
    mock_client.embed_query.return_value = [0.1] * 768

    with patch.object(provider, "get_embeddings_client", return_value=mock_client):
        result = provider.embed_query("Test-Anfrage")

    assert result == [0.1] * 768
    mock_client.embed_query.assert_called_once_with(
        "Test-Anfrage",
        output_dimensionality=768,
    )


def test_gemini_provider_embed_documents_uses_configured_dimension() -> None:
    settings = Settings(
        gemini_api_key="mock_key",
        gemini_embedding_dimension=768,
    )
    provider = GeminiProvider(settings)

    mock_client = MagicMock()
    mock_client.embed_documents.return_value = [[0.1] * 768, [0.2] * 768]

    with patch.object(provider, "get_embeddings_client", return_value=mock_client):
        result = provider.embed_documents(["Dokument 1", "Dokument 2"])

    assert len(result) == 2
    mock_client.embed_documents.assert_called_once_with(
        ["Dokument 1", "Dokument 2"],
        output_dimensionality=768,
    )


def test_gemini_provider_generate_text_invokes_llm() -> None:
    settings = Settings(
        gemini_api_key="mock_key",
        gemini_chat_model="gemini-3.8-flash",
    )
    provider = GeminiProvider(settings)

    mock_llm = MagicMock()
    mock_response = MagicMock()
    mock_response.content = "   Grounded answer from Gemini   "
    mock_llm.invoke.return_value = mock_response

    with patch.object(provider, "get_llm_client", return_value=mock_llm):
        result = provider.generate_text("Prompt question")

    assert result == "Grounded answer from Gemini"
    mock_llm.invoke.assert_called_once_with("Prompt question")


def test_rag_service_delegates_to_injected_provider() -> None:
    settings = Settings()

    class MockCustomProvider(AIProvider):
        @property
        def name(self) -> str:
            return "custom-mock"

        @property
        def is_configured(self) -> bool:
            return True

        def embed_query(self, text: str) -> list[float]:
            return [0.42] * 128

        def embed_documents(self, texts: list[str]) -> list[list[float]]:
            return [[0.42] * 128 for _ in texts]

        def generate_text(self, prompt: str) -> str:
            return "Custom provider response"

    mock_provider = MockCustomProvider()
    rag_service = RagService(settings, provider=mock_provider)

    assert rag_service.get_query_embedding("Query") == [0.42] * 128
    assert rag_service.get_documents_embeddings(["Doc1", "Doc2"]) == [[0.42] * 128, [0.42] * 128]


def test_factory_get_ai_provider_resolution_and_registration() -> None:
    settings = Settings(ai_provider="gemini", gemini_api_key="key")
    provider = get_ai_provider(settings)
    assert isinstance(provider, GeminiProvider)
    assert provider.name == "gemini"

    # Unknown provider raises ValueError
    with pytest.raises(ValueError, match="Unknown AI provider 'non_existent'"):
        get_ai_provider(settings, provider_name="non_existent")

    # Custom provider registration
    class DummyProvider(AIProvider):
        @property
        def name(self) -> str:
            return "dummy"

        @property
        def is_configured(self) -> bool:
            return True

        def embed_query(self, text: str) -> list[float]:
            return []

        def embed_documents(self, texts: list[str]) -> list[list[float]]:
            return []

        def generate_text(self, prompt: str) -> str:
            return "dummy"

    register_ai_provider("dummy", lambda s: DummyProvider())
    resolved = get_ai_provider(settings, provider_name="dummy")
    assert isinstance(resolved, DummyProvider)
