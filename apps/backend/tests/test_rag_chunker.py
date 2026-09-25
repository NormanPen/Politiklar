"""Unit tests for RAG chunking logic."""

from datetime import datetime, timezone
from uuid import uuid4

from db.relational.models import ParliamentarySpeech
from rag.chunker import chunk_speech


def test_chunk_speech_preserves_metadata_and_computes_sha256() -> None:
    source_doc_id = uuid4()
    speech_id = uuid4()
    speech = ParliamentarySpeech(
        id=speech_id,
        protocol_source_document_id=source_doc_id,
        electoral_term=21,
        sitting_number=42,
        speech_locator="Plenarprotokoll 21/42, Rede 5",
        first_name="Erika",
        last_name="Mustermann",
        parliamentary_group="Fraktion A",
        text="Sehr geehrte Frau Präsidentin, liebe Kolleginnen und Kollegen! " * 20,
        content_sha256="fake_sha",
        observed_at=datetime.now(timezone.utc),
    )

    chunks = chunk_speech(speech, chunk_size=200, chunk_overlap=20)

    assert len(chunks) > 1
    for chunk in chunks:
        assert chunk.content
        assert len(chunk.content_sha256) == 64
        assert chunk.metadata["source_document_id"] == str(source_doc_id)
        assert chunk.metadata["speech_id"] == str(speech_id)
        assert chunk.metadata["electoral_term"] == 21
        assert chunk.metadata["speaker_name"] == "Erika Mustermann"
        assert chunk.metadata["parliamentary_group"] == "Fraktion A"
        assert chunk.metadata["speech_locator"] == "Plenarprotokoll 21/42, Rede 5"
