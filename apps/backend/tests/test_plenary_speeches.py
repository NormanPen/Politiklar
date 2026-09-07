from crawler.plenary_speeches import parse_plenary_protocol


def test_parser_extracts_source_native_speaker_and_speech() -> None:
    protocol = b"""<dbtplenarprotokoll><vorspann><kopfdaten><dokumente><dokument><dateiname>21090.xml</dateiname></dokument></dokumente></kopfdaten></vorspann><rede id=\"ID219000100\"><p klasse=\"redner\"><redner id=\"11004011\"><name><vorname>Steffen</vorname><nachname>Bilger</nachname><fraktion>CDU/CSU</fraktion></name></redner></p><p klasse=\"J_1\">Amtlicher Redetext.</p></rede></dbtplenarprotokoll>"""

    result = parse_plenary_protocol(protocol)

    assert (result.electoral_term, result.sitting_number) == (21, 90)
    assert result.speeches[0].speaker_source_id == "11004011"
    assert result.speeches[0].text == "Amtlicher Redetext."