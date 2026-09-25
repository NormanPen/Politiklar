"""Gemini embeddings integration using langchain-google-genai."""

from langchain_google_genai import GoogleGenerativeAIEmbeddings

from core.settings import Settings


def get_embeddings_client(settings: Settings) -> GoogleGenerativeAIEmbeddings:
    """Returns a configured GoogleGenerativeAIEmbeddings instance."""
    if not settings.gemini_api_key:
        raise ValueError("GEMINI_API_KEY is not configured in settings.")
    return GoogleGenerativeAIEmbeddings(
        model=settings.gemini_embedding_model,
        google_api_key=settings.gemini_api_key,
    )
