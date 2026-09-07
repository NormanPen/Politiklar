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