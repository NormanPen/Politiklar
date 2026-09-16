"""Command-line entry points for source retrieval and member imports."""

import argparse
import json
from time import sleep

from sqlalchemy import select

from db.relational.models import BundestagMember
from .bundestag_biography import parse_biography_page
from .fetcher import fetch_document, fetch_source
from .bundestag_import import run_bundestag_import
from .member_images import fetch_and_import_member_image
from .member_importer import import_biography
from .member_source_identifiers import verify_plenary_speaker
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
    import_parser.add_argument("--no-images", action="store_true", help="Skip retrieving Wikimedia portraits")
    image_parser = subparsers.add_parser("import-member-image", help="Retrieve and import member portrait from Wikimedia Commons")
    image_parser.add_argument("url", help="Bundestag biography URL ending in an MDB ID")
    sync_images_parser = subparsers.add_parser("sync-member-images", help="Retrieve Wikimedia portraits for stored members missing an image")
    sync_images_parser.add_argument("--limit", type=int, help="Maximum number of members to process")
    vote_parser = subparsers.add_parser("import-named-vote", help="Import one official Bundestag named-vote XLSX list")
    vote_parser.add_argument("url", help="Official Bundestag XLSX URL")
    vote_parser.add_argument("--title", help="Official vote title from the source list")
    speech_parser = subparsers.add_parser("import-protocol", help="Import one official Bundestag plenary protocol XML")
    speech_parser.add_argument("url", help="Official Bundestag protocol XML URL")
    verify_parser = subparsers.add_parser("verify-plenary-speaker", help="Record a reviewed official mapping for a protocol speaker ID")
    verify_parser.add_argument("--mdb-id", type=int, required=True, help="Verified Bundestag MDB ID")
    verify_parser.add_argument("--speaker-id", required=True, help="Official speaker ID from a plenary protocol")
    verify_parser.add_argument("--biography-evidence-url", required=True, help="Official Bundestag biography URL for the MDB ID")
    verify_parser.add_argument("--protocol-evidence-url", required=True, help="Official protocol URL containing the speaker ID")
    verify_parser.add_argument("--verified-by", required=True, help="Reviewer name or service account")
    all_parser = subparsers.add_parser("import-all", help="Import all discoverable official Bundestag sources")
    all_parser.add_argument("--dry-run", action="store_true", help="Discover sources without importing them")
    all_parser.add_argument("--limit", type=int, help="Maximum sources to process per source family")
    all_parser.add_argument("--refresh", action="store_true", help="Run the idempotent refresh mode")
    all_parser.add_argument("--family", choices=["members", "votes", "protocols"], help="Restrict import to a specific source family")
    arguments = parser.parse_args()

    if arguments.command == "fetch":
        source = fetch_source(arguments.url)
        print(json.dumps(source.to_dict(), ensure_ascii=False, indent=2))
        return

    settings = Settings()
    session_factory = create_session_factory(settings)
    with session_factory() as session:
        if arguments.command == "import-biography":
            biography = import_biography(session, arguments.url, settings=settings, with_image=not arguments.no_images)
            result = {"mdb_id": biography.mdb_id, "status": "imported"}
        elif arguments.command == "import-member-image":
            document = fetch_document(arguments.url, settings)
            biography = parse_biography_page(document.content.decode("utf-8"), document.source.source_url)
            member = session.scalar(select(BundestagMember).where(BundestagMember.mdb_id == biography.mdb_id))
            if member is None:
                import_biography(session, arguments.url, settings=settings, with_image=True)
                member = session.scalar(select(BundestagMember).where(BundestagMember.mdb_id == biography.mdb_id))
            candidate = fetch_and_import_member_image(session, member, biography, settings)
            session.commit()
            result = {
                "mdb_id": biography.mdb_id,
                "wikidata_qid": candidate.wikidata_qid if candidate else None,
                "media_url": candidate.media_url if candidate else None,
                "license_name": candidate.license_name if candidate else None,
                "status": candidate.status if candidate else "not_found",
            }
        elif arguments.command == "sync-member-images":
            from db.relational.models import MemberImageCandidate, MemberProfileSnapshot, SourceDocument
            members = session.scalars(select(BundestagMember).order_by(BundestagMember.mdb_id.asc())).all()
            synced = 0
            found = 0
            for member in members:
                if arguments.limit and synced >= arguments.limit:
                    break
                has_approved = session.scalar(
                    select(MemberImageCandidate.id).where(
                        MemberImageCandidate.member_id == member.id,
                        MemberImageCandidate.status == "approved",
                    )
                )
                if has_approved is not None:
                    continue
                profile = session.scalar(
                    select(MemberProfileSnapshot).where(
                        MemberProfileSnapshot.member_id == member.id,
                        MemberProfileSnapshot.is_current.is_(True),
                    )
                )
                if not profile:
                    continue
                source = session.scalar(select(SourceDocument).where(SourceDocument.id == profile.source_document_id))
                if not source or not source.resolved_url:
                    continue
                try:
                    document = fetch_document(source.resolved_url, settings)
                    biography = parse_biography_page(document.content.decode("utf-8"), document.source.source_url)
                    candidate = fetch_and_import_member_image(session, member, biography, settings)
                    session.commit()
                    synced += 1
                    if candidate and candidate.status == "approved":
                        found += 1
                    sleep(1.0)
                except Exception:
                    session.rollback()
            result = {"processed": synced, "images_found": found}
        elif arguments.command == "import-named-vote":
            vote = import_named_vote(session, arguments.url, arguments.title)
            result = {"electoral_term": vote.electoral_term, "sitting_number": vote.sitting_number, "vote_number": vote.vote_number, "rows": len(vote.rows), "status": "imported"}
        elif arguments.command == "import-protocol":
            protocol = import_plenary_protocol(session, arguments.url)
            result = {"electoral_term": protocol.electoral_term, "sitting_number": protocol.sitting_number, "speeches": len(protocol.speeches), "status": "imported"}
        elif arguments.command == "verify-plenary-speaker":
            mapping = verify_plenary_speaker(session, arguments.mdb_id, arguments.speaker_id, arguments.biography_evidence_url, arguments.protocol_evidence_url, arguments.verified_by)
            result = {"mdb_id": arguments.mdb_id, "speaker_source_id": mapping.source_identifier, "status": mapping.verification_status}
        else:
            result = run_bundestag_import(
                session,
                settings,
                dry_run=arguments.dry_run,
                limit=arguments.limit,
                refresh=arguments.refresh,
                family=arguments.family,
            ).to_dict()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()