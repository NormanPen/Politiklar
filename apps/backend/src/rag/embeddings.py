"""Gemini embeddings integration delegating to GeminiProvider for backwards compatibility."""

from langchain_google_genai import GoogleGenerativeAIEmbeddings

from core.settings import Settings
from .providers.gemini import GeminiProvider


def get_embeddings_client(settings: Settings) -> GoogleGenerativeAIEmbeddings:
    """Returns a configured GoogleGenerativeAIEmbeddings instance."""
    provider = GeminiProvider(settings)
    return provider.get_embeddings_client()

