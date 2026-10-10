"""Unit tests for the politiklar-rag CLI tool."""

import json
from unittest.mock import MagicMock, patch

from core.settings import Settings
from rag.cli import main


def test_cli_info_command(capsys) -> None:
    test_settings = Settings(ai_provider="gemini", gemini_api_key="mock_key")

    with (
        patch("sys.argv", ["politiklar-rag", "info"]),
        patch("rag.cli.Settings", return_value=test_settings),
    ):
        main()

    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["provider"] == "gemini"
    assert data["is_configured"] is True
    assert data["chat_model"] == "gemini-3.8-flash"


def test_cli_embed_command(capsys) -> None:
    mock_provider = MagicMock()
    mock_provider.name = "gemini"
    mock_provider.is_configured = True
    mock_provider.embed_query.return_value = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]

    with (
        patch("sys.argv", ["politiklar-rag", "embed", "Beispieltext"]),
        patch("rag.cli.get_ai_provider", return_value=mock_provider),
    ):
        main()

    captured = capsys.readouterr()
    assert "Dimension: 6" in captured.out
    mock_provider.embed_query.assert_called_once_with("Beispieltext")


def test_cli_generate_command(capsys) -> None:
    mock_provider = MagicMock()
    mock_provider.name = "gemini"
    mock_provider.is_configured = True
    mock_provider.generate_text.return_value = "Generierte Antwort"

    with (
        patch("sys.argv", ["politiklar-rag", "generate", "Was ist Politiklar?"]),
        patch("rag.cli.get_ai_provider", return_value=mock_provider),
    ):
        main()

    captured = capsys.readouterr()
    assert "Generierte Antwort" in captured.out
    mock_provider.generate_text.assert_called_once_with("Was ist Politiklar?")
