"""Chunking logic for parliamentary speeches and official documents."""

from dataclasses import dataclass
import hashlib
from typing import Any

from langchain_text_splitters import RecursiveCharacterTextSplitter

from db.relational.models import ParliamentarySpeech


@dataclass(frozen=True)
class SpeechChunk:
    chunk_index: int
    content: str
    content_sha256: str
    metadata: dict[str, Any]


def chunk_speech(
    speech: ParliamentarySpeech,
    chunk_size: int = 1000,
    chunk_overlap: int = 150,
) -> list[SpeechChunk]:
    """Splits a parliamentary speech into context-preserving chunks with official metadata."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    raw_chunks = splitter.split_text(speech.text)
    speaker_name = f"{speech.first_name or ''} {speech.last_name or ''}".strip() or "Unbekannt"

    chunks: list[SpeechChunk] = []
    for idx, content in enumerate(raw_chunks):
        cleaned_content = content.strip()
        if not cleaned_content:
            continue
        content_hash = hashlib.sha256(cleaned_content.encode("utf-8")).hexdigest()
        metadata = {
            "source_document_id": str(speech.protocol_source_document_id),
            "speech_id": str(speech.id),
            "speech_locator": speech.speech_locator,
            "electoral_term": speech.electoral_term,
            "sitting_number": speech.sitting_number,
            "speaker_name": speaker_name,
            "parliamentary_group": speech.parliamentary_group,
            "observed_at": speech.observed_at.isoformat() if speech.observed_at else None,
        }
        chunks.append(
            SpeechChunk(
                chunk_index=idx,
                content=cleaned_content,
                content_sha256=content_hash,
                metadata=metadata,
            )
        )
    return chunks
