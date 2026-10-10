"""Politiklar MCP Server instance and tool registrations using MCPServer."""

from collections.abc import Callable
from typing import Any

from mcp.server.mcpserver import MCPServer
from sqlalchemy.orm import Session, sessionmaker

from core.settings import Settings
from db.relational.session import create_session_factory
from .tools.rag_tools import query_bundestag_rag, query_speeches_semantic
from .tools.sql_tools import list_recent_named_votes, query_member_profile, query_named_vote

SERVER_INSTRUCTIONS = """
Offizieller parlamentarischer KI-Assistent für Daten des Deutschen Bundestages (Politiklar).
Bietet verifizierte Werkzeuge für:
1. get_member_profile: Offizielle Abgeordneten-Biografien, Fraktion, Mandat und Nebentätigkeiten (SQL).
2. get_named_vote: Amtliche Ergebnisse namentlicher Abstimmungen inklusive Fraktionsaufteilung (SQL).
3. list_named_votes: Übersicht kürzlicher namentlicher Abstimmungen (SQL).
4. ask_bundestag_rag: Beantwortung von Bürger- und Recherchefragen mit primärquellenbasierten Belegen aus Plenarprotokollen (RAG).
5. search_speeches: Semantische Vektorsuche in Bundestagsreden zur Textrecherche (pgvector).
""".strip()


def create_mcp_server(
    settings: Settings | None = None,
    session_factory: sessionmaker[Session] | Callable[[], Session] | None = None,
) -> MCPServer:
    """Creates and configures a Politiklar MCPServer instance with all tools registered."""
    app_settings = settings or Settings()
    app_session_factory = session_factory or create_session_factory(app_settings)

    server = MCPServer(
        name="politiklar",
        instructions=SERVER_INSTRUCTIONS,
        version="0.1.0",
    )

    def _get_session() -> Session:
        return app_session_factory()

    @server.tool(
        description="Ruft das offizielle Profil eines Bundestagsabgeordneten ab (Name, Fraktion, Wahlkreis, Biografie, Nebentätigkeiten)."
    )
    def get_member_profile(name_or_mdb_id: str) -> dict[str, Any]:
        with _get_session() as session:
            return query_member_profile(session, name_or_mdb_id)

    @server.tool(
        description="Ruft das amtliche Gesamtergebnis einer namentlichen Abstimmung im Bundestag ab (Ja/Nein/Enthalten/Nicht abgegeben)."
    )
    def get_named_vote(title_or_id: str) -> dict[str, Any]:
        with _get_session() as session:
            return query_named_vote(session, title_or_id)

    @server.tool(
        description="Listet kürzlich durchgeführte namentliche Abstimmungen des Bundestages auf."
    )
    def list_named_votes(limit: int = 10, electoral_term: int = 21) -> list[dict[str, Any]]:
        with _get_session() as session:
            return list_recent_named_votes(session, limit=limit, electoral_term=electoral_term)

    @server.tool(
        description="Beantwortet Bürger- und Sachfragen evidenzbasiert anhand von Plenarprotokollen und Reden mit konkreten Quellenverweisen (RAG)."
    )
    def ask_bundestag_rag(question: str) -> dict[str, Any]:
        with _get_session() as session:
            return query_bundestag_rag(session, app_settings, question)

    @server.tool(
        description="Führt eine semantische Vektorsuche nach Reden im Bundestag durch und liefert relevante Zitate mit Ähnlichkeitsscores."
    )
    def search_speeches(query: str, limit: int = 5) -> list[dict[str, Any]]:
        with _get_session() as session:
            return query_speeches_semantic(session, app_settings, query, limit=limit)

    return server
