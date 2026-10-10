"""Retrieval-Augmented Generation (RAG) module for Politiklar."""

from .chunker import chunk_speech, SpeechChunk
from .embeddings import get_embeddings_client
from .prompts import RAG_SYSTEM_PROMPT
from .providers import (
    AIProvider,
    EmbeddingProvider,
    GeminiProvider,
    LLMProvider,
    get_ai_provider,
    register_ai_provider,
)
from .service import RagService

__all__ = [
    "AIProvider",
    "EmbeddingProvider",
    "GeminiProvider",
    "LLMProvider",
    "get_ai_provider",
    "register_ai_provider",
    "chunk_speech",
    "SpeechChunk",
    "get_embeddings_client",
    "RAG_SYSTEM_PROMPT",
    "RagService",
]

