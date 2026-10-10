"""Unit tests for the Politiklar MCP Server and tools."""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from uuid import uuid4
import pytest

from core.settings import Settings
from db.relational.models import (
    BundestagMember,
    MemberAffiliation,
    MemberMandate,
    MemberProfileSnapshot,
    NamedVote,
    NamedVoteRow,
    SourceDocument,
)
from mcp_server.server import create_mcp_server
from mcp_server.tools.sql_tools import (
    list_recent_named_votes,
    query_member_profile,
    query_named_vote,
)
from mcp_server.tools.rag_tools import (
    query_bundestag_rag,
    query_speeches_semantic,
)


@pytest.mark.anyio
async def test_mcp_server_lists_all_five_tools(db_session) -> None:
    settings = Settings(gemini_api_key="mock_key")
    server = create_mcp_server(settings=settings, session_factory=lambda: db_session)

    tools = await server.list_tools()
    tool_names = {t.name for t in tools}

    expected_tools = {
        "get_member_profile",
        "get_named_vote",
        "list_named_votes",
        "ask_bundestag_rag",
        "search_speeches",
    }
    assert expected_tools.issubset(tool_names)


def test_query_member_profile_not_found(db_session) -> None:
    result = query_member_profile(db_session, "UnbekannterPolitiker")
    assert result["found"] is False
    assert "Kein Abgeordneter gefunden" in result["message"]


def test_query_member_profile_found_by_mdb_id_and_name(db_session) -> None:
    source = SourceDocument(
        id=uuid4(),
        publisher="Bundestag",
        requested_url="https://example.com/source",
        resolved_url="https://example.com/source",
        retrieved_at=datetime.now(timezone.utc),
        status_code=200,
        content_type="text/html",
        content_sha256="fakehash123",
        retrieval_tool="test",
    )
    db_session.add(source)

    member = BundestagMember(id=uuid4(), mdb_id=99999)
    db_session.add(member)
    db_session.flush()

    snapshot = MemberProfileSnapshot(
        id=uuid4(),
        member_id=member.id,
        source_document_id=source.id,
        observed_at=datetime.now(timezone.utc),
        first_name="Max",
        last_name="Mustermann",
        parliamentary_group="Fraktion Test",
        occupation="Diplom-Ingenieur",
        content_sha256="snaphash123",
        is_current=True,
    )
    db_session.add(snapshot)

    mandate = MemberMandate(
        id=uuid4(),
        member_id=member.id,
        source_document_id=source.id,
        mandate_type="Direktmandat",
        constituency_number=42,
        constituency_name="Muster-Wahlkreis",
        content_sha256="mandatehash123",
        observed_at=datetime.now(timezone.utc),
    )
    db_session.add(mandate)

    affiliation = MemberAffiliation(
        id=uuid4(),
        member_id=member.id,
        source_document_id=source.id,
        category="Aufsichtsrat",
        organization_name="Muster AG",
        role_name="Mitglied",
        content_sha256="affilhash123",
        observed_at=datetime.now(timezone.utc),
    )
    db_session.add(affiliation)
    db_session.commit()

    # Query by mdb_id
    res_id = query_member_profile(db_session, "99999")
    assert res_id["found"] is True
    assert res_id["name"] == "Max Mustermann"
    assert res_id["parliamentary_group"] == "Fraktion Test"
    assert len(res_id["mandates"]) == 1
    assert res_id["mandates"][0]["constituency_name"] == "Muster-Wahlkreis"
    assert len(res_id["affiliations"]) == 1
    assert res_id["affiliations"][0]["organization"] == "Muster AG"

    # Query by name
    res_name = query_member_profile(db_session, "Mustermann")
    assert res_name["found"] is True
    assert res_name["mdb_id"] == 99999


def test_query_named_vote_and_listing(db_session) -> None:
    source = SourceDocument(
        id=uuid4(),
        publisher="Bundestag",
        requested_url="https://example.com/vote-source",
        resolved_url="https://example.com/vote-source",
        retrieved_at=datetime.now(timezone.utc),
        status_code=200,
        content_type="application/vnd.openxmlformats",
        content_sha256="votehash123",
        retrieval_tool="test",
    )
    db_session.add(source)

    vote = NamedVote(
        id=uuid4(),
        source_document_id=source.id,
        electoral_term=21,
        sitting_number=10,
        vote_number=1,
        title="Gesetz zur Förderung von Transparenz",
        content_sha256="votecontent123",
        retrieved_at=datetime.now(timezone.utc),
    )
    db_session.add(vote)
    db_session.flush()

    row1 = NamedVoteRow(
        id=uuid4(),
        named_vote_id=vote.id,
        source_document_id=source.id,
        raw_outcome="ja",
        outcome="yes",
        parliamentary_group="Fraktion A",
        content_sha256="row1",
        observed_at=datetime.now(timezone.utc),
    )
    row2 = NamedVoteRow(
        id=uuid4(),
        named_vote_id=vote.id,
        source_document_id=source.id,
        raw_outcome="nein",
        outcome="no",
        parliamentary_group="Fraktion B",
        content_sha256="row2",
        observed_at=datetime.now(timezone.utc),
    )
    db_session.add_all([row1, row2])
    db_session.commit()

    # Search vote
    vote_res = query_named_vote(db_session, "Transparenz")
    assert vote_res["found"] is True
    assert vote_res["electoral_term"] == 21
    assert vote_res["results_summary"]["yes"] == 1
    assert vote_res["results_summary"]["no"] == 1
    assert "Fraktion A" in vote_res["fraction_breakdown"]

    # List votes
    votes_list = list_recent_named_votes(db_session, limit=5, electoral_term=21)
    assert len(votes_list) >= 1
    assert votes_list[0]["title"] == "Gesetz zur Förderung von Transparenz"


def test_query_bundestag_rag_tool(db_session) -> None:
    settings = Settings(gemini_api_key="mock_key")
    mock_response = MagicMock()
    mock_response.question = "Wie sieht die Lage aus?"
    mock_response.answer = "Laut Plenarprotokoll 21/10 positiv."
    mock_response.is_sufficient_evidence = True
    mock_response.citations = [{"locator": "Plenarprotokoll 21/10", "speaker": "Abg. Schmidt"}]
    mock_response.chunks = [MagicMock()]

    with patch("mcp_server.tools.rag_tools.RagService") as mock_service_cls:
        instance = mock_service_cls.return_value
        instance.provider.is_configured = True
        instance.generate_answer.return_value = mock_response

        res = query_bundestag_rag(db_session, settings, "Wie sieht die Lage aus?")

    assert res["is_sufficient_evidence"] is True
    assert "positiv" in res["answer"]
    assert len(res["citations"]) == 1


def test_query_speeches_semantic_tool(db_session) -> None:
    settings = Settings(gemini_api_key="mock_key")
    mock_chunk = MagicMock()
    mock_chunk.chunk_id = uuid4()
    mock_chunk.source_document_id = uuid4()
    mock_chunk.metadata = {"speaker_name": "Erika Mustermann", "speech_locator": "TOP 3"}
    mock_chunk.similarity_score = 0.92
    mock_chunk.content = "Ausschnitt aus der Rede zur Bildungspolitik."

    with patch("mcp_server.tools.rag_tools.RagService") as mock_service_cls:
        instance = mock_service_cls.return_value
        instance.provider.is_configured = True
        instance.get_query_embedding.return_value = [0.1] * 768
        instance.search_similar_chunks.return_value = [mock_chunk]

        results = query_speeches_semantic(db_session, settings, "Bildungspolitik", limit=3)

    assert len(results) == 1
    assert results[0]["speaker"] == "Erika Mustermann"
    assert results[0]["similarity_score"] == 0.92
    assert "Bildungspolitik" in results[0]["content"]
