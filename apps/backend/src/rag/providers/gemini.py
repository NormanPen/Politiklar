"""Google Gemini AI provider implementation using langchain-google-genai."""

from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

from core.settings import Settings
from .base import AIProvider


class GeminiProvider(AIProvider):
    """AI Provider implementation for Google Gemini."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._llm_client: ChatGoogleGenerativeAI | None = None
        self._embeddings_client: GoogleGenerativeAIEmbeddings | None = None

    @property
    def name(self) -> str:
        return "gemini"

    @property
    def is_configured(self) -> bool:
        return bool(self.settings.gemini_api_key and self.settings.gemini_api_key.strip())

    def get_llm_client(self) -> ChatGoogleGenerativeAI:
        """Returns the configured ChatGoogleGenerativeAI client."""
        if not self.is_configured:
            raise ValueError("GEMINI_API_KEY is not configured in settings.")
        if self._llm_client is None:
            self._llm_client = ChatGoogleGenerativeAI(
                model=self.settings.gemini_chat_model,
                google_api_key=self.settings.gemini_api_key,
                temperature=0.0,
                max_retries=0,
                timeout=10.0,
            )
        return self._llm_client

    def get_embeddings_client(self) -> GoogleGenerativeAIEmbeddings:
        """Returns the configured GoogleGenerativeAIEmbeddings client."""
        if not self.is_configured:
            raise ValueError("GEMINI_API_KEY is not configured in settings.")
        if self._embeddings_client is None:
            self._embeddings_client = GoogleGenerativeAIEmbeddings(
                model=self.settings.gemini_embedding_model,
                google_api_key=self.settings.gemini_api_key,
                max_retries=0,
            )
        return self._embeddings_client

    def embed_query(self, text: str) -> list[float]:
        """Generates embedding vector for a single query text."""
        client = self.get_embeddings_client()
        return client.embed_query(
            text,
            output_dimensionality=self.settings.gemini_embedding_dimension,
        )

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Generates embedding vectors for document chunks."""
        client = self.get_embeddings_client()
        return client.embed_documents(
            texts,
            output_dimensionality=self.settings.gemini_embedding_dimension,
        )

    def generate_text(self, prompt: str) -> str:
        """Generates grounded answer text using ChatGoogleGenerativeAI."""
        llm = self.get_llm_client()
        response = llm.invoke(prompt)
        return str(response.content).strip()
