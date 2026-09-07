from crawler.bundestag_import import _links_with_fragment


def test_discovery_extracts_only_matching_official_links() -> None:
    html = """
    <a href="https://www.bundestag.de/abgeordnete/biografien/A/example-1043330">Profile</a>
    <a href="https://www.bundestag.de/resource/blob/1/vote.xlsx">Vote</a>
    <a href="https://example.invalid/abgeordnete/biografien/A/other-1">Other</a>
    """

    assert _links_with_fragment(html, "/abgeordnete/biografien/") == [
        "https://www.bundestag.de/abgeordnete/biografien/A/example-1043330",
        "https://example.invalid/abgeordnete/biografien/A/other-1",
    ]


def test_discovery_resolves_relative_links() -> None:
    html = '<a href="/abgeordnete/biografien/A/example-1043330">Profile</a>'
    assert _links_with_fragment(html, "/abgeordnete/biografien/", base_url="https://www.bundestag.de/ajax/...") == [
        "https://www.bundestag.de/abgeordnete/biografien/A/example-1043330",
    ]


def test_discover_links_paginates_with_official_headers(monkeypatch) -> None:
    from core.settings import Settings
    from crawler.bundestag_import import discover_links
    from crawler.fetcher import FetchedDocument, FetchedSource

    calls: list[str] = []

    def mock_fetch_document(url: str, settings: Settings) -> FetchedDocument:
        calls.append(url)
        if "offset=0" in url:
            html = """
            <a href="https://www.bundestag.de/abgeordnete/biografien/A/person-1">P1</a>
            <a href="https://www.bundestag.de/abgeordnete/biografien/A/person-2">P2</a>
            """
            headers = {"hits-count": "3", "loaded-count": "2"}
        elif "offset=2" in url:
            html = """
            <a href="https://www.bundestag.de/abgeordnete/biografien/A/person-3">P3</a>
            """
            headers = {"hits-count": "3", "loaded-count": "1"}
        else:
            html = ""
            headers = {"hits-count": "3", "loaded-count": "0"}

        return FetchedDocument(
            source=FetchedSource(
                source_url=url,
                retrieved_at="2026-09-07T00:00:00Z",
                status_code=200,
                content_type="text/html",
                content_sha256="dummy",
                title="Test",
            ),
            content=html.encode("utf-8"),
            response_headers=headers,
            snapshot_location=None,
        )

    monkeypatch.setattr("crawler.bundestag_import.fetch_document", mock_fetch_document)

    settings = Settings(database_url="sqlite://", crawler_requests_per_second=100.0)
    discovered = discover_links("https://www.bundestag.de/endpoint", "/abgeordnete/biografien/", settings)

    assert discovered == [
        "https://www.bundestag.de/abgeordnete/biografien/A/person-1",
        "https://www.bundestag.de/abgeordnete/biografien/A/person-2",
        "https://www.bundestag.de/abgeordnete/biografien/A/person-3",
    ]
    assert calls == [
        "https://www.bundestag.de/endpoint?offset=0",
        "https://www.bundestag.de/endpoint?offset=2",
    ]


def test_discover_links_respects_limit(monkeypatch) -> None:
    from core.settings import Settings
    from crawler.bundestag_import import discover_links
    from crawler.fetcher import FetchedDocument, FetchedSource

    calls: list[str] = []

    def mock_fetch_document(url: str, settings: Settings) -> FetchedDocument:
        calls.append(url)
        html = """
        <a href="https://www.bundestag.de/abgeordnete/biografien/A/person-1">P1</a>
        <a href="https://www.bundestag.de/abgeordnete/biografien/A/person-2">P2</a>
        """
        return FetchedDocument(
            source=FetchedSource(
                source_url=url,
                retrieved_at="2026-09-07T00:00:00Z",
                status_code=200,
                content_type="text/html",
                content_sha256="dummy",
                title="Test",
            ),
            content=html.encode("utf-8"),
            response_headers={"hits-count": "100", "loaded-count": "2"},
            snapshot_location=None,
        )

    monkeypatch.setattr("crawler.bundestag_import.fetch_document", mock_fetch_document)

    settings = Settings(database_url="sqlite://", crawler_requests_per_second=100.0)
    discovered = discover_links("https://www.bundestag.de/endpoint", "/abgeordnete/biografien/", settings, limit=1)

    assert discovered == ["https://www.bundestag.de/abgeordnete/biografien/A/person-1"]
    assert len(calls) == 1