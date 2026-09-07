from crawler.bundestag_biography import parse_biography_page


def test_profile_hash_ignores_unrelated_html_changes() -> None:
    page = """
    <script type="application/ld+json">{"@type":"ProfilePage","mainEntity":{"@type":"Person","givenName":"Sanae","familyName":"Abdi","memberOf":[{"@type":"Role","roleName":"Mitglied des Bundestages","startDate":"2025-03-25","memberOf":{"name":"Deutscher Bundestag","url":"https://www.bundestag.de"}},{"@type":"Role","roleName":"Ordentliches Mitglied","startDate":"2025-03-25","memberOf":{"name":"Ausschuss für Digitales","url":"https://www.bundestag.de/ausschuesse/digitales"}}]}}</script>
    <section class="m-biography__intro"><h1 class="m-biography__introName">Sanae Abdi</h1><p class="m-biography__introInfo"><span>Managerin</span><strong>SPD</strong></p></section><div class="m-marginal__itemContent"><a title="Kontakt" href="/services/formular/contactform?mdbId=1043330">Kontakt</a></div><div class="m-biography__constituencyInfoItem"><p class="m-biography__constituencyInfoItemTitle"><strong>Wahlkreismandat</strong></p><a href="/abgeordnete/wahlkreissuche?wknr=092">Wahlkreis 092: Köln I, Nordrhein-Westfalen</a></div>
    """

    first = parse_biography_page(page, "https://www.bundestag.de/abgeordnete/biografien/A/abdi_sanae-1043330")
    second = parse_biography_page(page + "<footer>Updated tracking markup</footer>", "https://www.bundestag.de/abgeordnete/biografien/A/abdi_sanae-1043330")

    assert first.content_sha256 == second.content_sha256
    assert first.mandate_start.isoformat() == "2025-03-25"
    assert first.affiliations[1].organization_name == "Ausschuss für Digitales"
    assert first.contact_points[0].url.endswith("mdbId=1043330")
    assert first.mandates[0].constituency_number == 92