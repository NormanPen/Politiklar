from pathlib import Path

from crawler.fetcher import _archive_content


def test_source_archive_is_content_addressed_and_idempotent(tmp_path: Path) -> None:
    content = b"official source content"
    content_hash = "ab" + "0" * 62

    first_path = _archive_content(content, content_hash, tmp_path)
    second_path = _archive_content(content, content_hash, tmp_path)

    assert first_path == second_path
    assert first_path == tmp_path / "ab" / content_hash
    assert first_path.read_bytes() == content