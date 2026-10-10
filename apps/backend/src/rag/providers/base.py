"""Base interfaces and abstract classes for AI providers (LLM and Embeddings)."""

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Abstract interface for text generation and chat models."""

    @abstractmethod
    def generate_text(self, prompt: str) -> str:
        """Generates a text completion/response for the given prompt."""
        ...


class EmbeddingProvider(ABC):
    """Abstract interface for text embeddings."""

    @abstractmethod
    def embed_query(self, text: str) -> list[float]:
        """Generates embedding vector for a single query text."""
        ...

    @abstractmethod
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Generates embedding vectors for a list of document chunk texts."""
        ...


class AIProvider(LLMProvider, EmbeddingProvider, ABC):
    """Unified AI provider combining LLM generation and embedding capabilities."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier of the provider (e.g. 'gemini', 'openai', 'ollama')."""
        ...

    @property
    @abstractmethod
    def is_configured(self) -> bool:
        """Whether the provider has valid configuration / API keys available."""
        ...
