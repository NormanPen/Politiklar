"""Command-line entry points for source retrieval and member imports."""

import argparse
import json

from .fetcher import fetch_source
from .member_importer import import_biography
from .named_votes import import_named_vote
from .plenary_speeches import import_plenary_protocol
from core.settings import Settings
from db.relational.session import create_session_factory


def main() -> None:
    parser = argparse.ArgumentParser(description="Retrieve or import official Bundestag source documents.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    fetch_parser = subparsers.add_parser("fetch", help="Retrieve source metadata")
    fetch_parser.add_argument("url", help="Official source URL to retrieve")
    import_parser = subparsers.add_parser("import-biography", help="Import one Bundestag biography page")
    import_parser.add_argument("url", help="Bundestag biography URL ending in an MDB ID")
    vote_parser = subparsers.add_parser("import-named-vote", help="Import one official Bundestag named-vote XLSX list")
    vote_parser.add_argument("url", help="Official Bundestag XLSX URL")
    vote_parser.add_argument("--title", help="Official vote title from the source list")
    speech_parser = subparsers.add_parser("import-protocol", help="Import one official Bundestag plenary protocol XML")
    speech_parser.add_argument("url", help="Official Bundestag protocol XML URL")
    arguments = parser.parse_args()

    if arguments.command == "fetch":
        source = fetch_source(arguments.url)
        print(json.dumps(source.to_dict(), ensure_ascii=False, indent=2))
        return

    session_factory = create_session_factory(Settings())
    with session_factory() as session:
        if arguments.command == "import-biography":
            biography = import_biography(session, arguments.url)
            result = {"mdb_id": biography.mdb_id, "status": "imported"}
        elif arguments.command == "import-named-vote":
            vote = import_named_vote(session, arguments.url, arguments.title)
            result = {"electoral_term": vote.electoral_term, "sitting_number": vote.sitting_number, "vote_number": vote.vote_number, "rows": len(vote.rows), "status": "imported"}
        else:
            protocol = import_plenary_protocol(session, arguments.url)
            result = {"electoral_term": protocol.electoral_term, "sitting_number": protocol.sitting_number, "speeches": len(protocol.speeches), "status": "imported"}
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()