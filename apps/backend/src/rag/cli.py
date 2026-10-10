"""Command-line interface for RAG and modular AI provider operations."""

import argparse
import json
import sys

from core.settings import Settings
from db.relational.session import create_session_factory
from rag.providers import get_ai_provider
from rag.service import RagService


def main() -> None:
    parser = argparse.ArgumentParser(description="Politiklar AI Provider & RAG CLI tool.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: info
    subparsers.add_parser("info", help="Display active AI provider status and configuration")

    # Subcommand: embed
    embed_parser = subparsers.add_parser("embed", help="Compute test embeddings with the active provider")
    embed_parser.add_argument("text", help="Text to vectorize")

    # Subcommand: generate
    generate_parser = subparsers.add_parser("generate", help="Generate response text directly via the provider LLM")
    generate_parser.add_argument("prompt", help="Prompt text")

    # Subcommand: ask
    ask_parser = subparsers.add_parser("ask", help="Execute an evidence-grounded RAG query against the database")
    ask_parser.add_argument("question", help="Citizen or parliamentary question")

    arguments = parser.parse_args()
    settings = Settings()
    provider = get_ai_provider(settings)

    if arguments.command == "info":
        info = {
            "provider": provider.name,
            "is_configured": provider.is_configured,
            "chat_model": getattr(settings, f"{provider.name}_chat_model", None),
            "embedding_model": getattr(settings, f"{provider.name}_embedding_model", None),
            "embedding_dimension": getattr(settings, f"{provider.name}_embedding_dimension", None),
        }
        print(json.dumps(info, indent=2))
        return

    if not provider.is_configured:
        print(
            f"Error: AI Provider '{provider.name}' is not configured. "
            f"Please check your environment variables (e.g. GEMINI_API_KEY).",
            file=sys.stderr,
        )
        sys.exit(1)

    if arguments.command == "embed":
        vector = provider.embed_query(arguments.text)
        print(f"Provider: {provider.name}")
        print(f"Dimension: {len(vector)}")
        print(f"Preview (first 5 elements): {vector[:5]}")

    elif arguments.command == "generate":
        response = provider.generate_text(arguments.prompt)
        print(response)

    elif arguments.command == "ask":
        session_factory = create_session_factory(settings)
        service = RagService(settings, provider=provider)
        with session_factory() as session:
            rag_res = service.generate_answer(session, arguments.question)
            output = {
                "question": rag_res.question,
                "answer": rag_res.answer,
                "is_sufficient_evidence": rag_res.is_sufficient_evidence,
                "citations": rag_res.citations,
                "chunks_count": len(rag_res.chunks),
            }
            print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
