"""Importer for official Bundestag plenary-protocol XML files."""

import xml.etree.ElementTree as element_tree
from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
from urllib.parse import urlparse

from sqlalchemy import select
from sqlalchemy.orm import Session

from db.relational.models import ParliamentarySpeech, SourceDocument

from .fetcher import FetchedDocument, fetch_document
from .named_votes import _get_or_create_source


@dataclass(frozen=True)
class ParsedSpeech:
    locator: str
    speaker_source_id: str | None
    first_name: str | None
    last_name: str | None
    parliamentary_group: str | None
    text: str


@dataclass(frozen=True)
class ParsedProtocol:
    electoral_term: int
    sitting_number: int
    speeches: tuple[ParsedSpeech, ...]


def parse_plenary_protocol(content: bytes, source_url: str | None = None) -> ParsedProtocol:
    root = element_tree.fromstring(content)
    electoral_term, sitting_number = _protocol_identifiers(root, source_url)
    speeches: list[ParsedSpeech] = []
    for speech in root.findall(".//rede"):
        locator = speech.get("id")
        speaker = speech.find(".//redner")
        if not locator or speaker is None:
            continue
        name = speaker.find("name")
        text = "\n".join("".join(paragraph.itertext()).strip() for paragraph in speech.findall("p") if paragraph.get("klasse") != "redner")
        if not text:
            continue
        speeches.append(ParsedSpeech(
            locator=locator,
            speaker_source_id=speaker.get("id"),
            first_name=_child_text(name, "vorname"),
            last_name=_child_text(name, "nachname"),
            parliamentary_group=_child_text(name, "fraktion"),
            text=text,
        ))
    return ParsedProtocol(electoral_term=electoral_term, sitting_number=sitting_number, speeches=tuple(speeches))


def import_plenary_protocol(session: Session, url: str) -> ParsedProtocol:
    document = fetch_document(url)
    protocol = parse_plenary_protocol(document.content, document.source.source_url)
    source = _get_or_create_source(session, url, document)
    for speech in protocol.speeches:
        content_hash = sha256(repr(speech).encode()).hexdigest()
        exists = session.scalar(select(ParliamentarySpeech.id).where(ParliamentarySpeech.protocol_source_document_id == source.id, ParliamentarySpeech.speech_locator == speech.locator, ParliamentarySpeech.content_sha256 == content_hash))
        if exists is None:
            session.add(ParliamentarySpeech(protocol_source_document_id=source.id, electoral_term=protocol.electoral_term, sitting_number=protocol.sitting_number, speech_locator=speech.locator, speaker_source_id=speech.speaker_source_id, first_name=speech.first_name, last_name=speech.last_name, parliamentary_group=speech.parliamentary_group, text=speech.text, content_sha256=content_hash, observed_at=datetime.fromisoformat(document.source.retrieved_at)))
    session.commit()
    return protocol


def _protocol_identifiers(root: element_tree.Element, source_url: str | None) -> tuple[int, int]:
    filename = (root.findtext(".//vorspann/kopfdaten/dokumente/dokument/dateiname") or "").removesuffix(".xml")
    if not filename and source_url:
        filename = urlparse(source_url).path.rsplit("/", maxsplit=1)[-1].removesuffix(".xml")
    if len(filename) >= 5 and filename[:2].isdigit() and filename[2:].isdigit():
        return int(filename[:2]), int(filename[2:])
    raise ValueError("The protocol does not expose a parseable official filename.")


def _child_text(element: element_tree.Element | None, tag: str) -> str | None:
    return element.findtext(tag) if element is not None else None