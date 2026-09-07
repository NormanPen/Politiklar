from io import BytesIO

from openpyxl import Workbook

from crawler.named_votes import parse_named_vote_xlsx


def test_parser_distinguishes_all_official_vote_outcomes() -> None:
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["Wahlperiode", "Sitzungnr", "Abstimmnr", "Fraktion/Gruppe", "Name", "Vorname", "Titel", "ja", "nein", "Enthaltung", "ungültig", "nichtabgegeben", "Bezeichnung", "Bemerkung"])
    sheet.append([21, 90, 8, "SPD", "Beispiel", "Ada", None, 1, 0, 0, 0, 0, "Ada Beispiel", None])
    sheet.append([21, 90, 8, "SPD", "Beispiel", "Bert", None, 0, 0, 1, 0, 0, "Bert Beispiel", None])
    sheet.append([21, 90, 8, "SPD", "Beispiel", "Cem", None, 0, 0, 0, 0, 1, "Cem Beispiel", None])
    buffer = BytesIO()
    workbook.save(buffer)

    vote = parse_named_vote_xlsx(buffer.getvalue())

    assert (vote.electoral_term, vote.sitting_number, vote.vote_number) == (21, 90, 8)
    assert [row.outcome for row in vote.rows] == ["yes", "abstained", "not_voted"]
    assert [row.raw_outcome for row in vote.rows] == ["ja", "enthaltung", "nichtabgegeben"]