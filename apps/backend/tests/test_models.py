"""Schema-level regression tests for source and portrait safeguards."""

from db.relational.models import MemberImageCandidate, MemberSourceIdentifier, MemberSourceIdentifierEvidence, SourceDocument


def test_source_documents_deduplicate_identical_source_content() -> None:
    constraint_names = {constraint.name for constraint in SourceDocument.__table__.constraints}

    assert "uq_source_document_content" in constraint_names


def test_approved_portraits_require_an_approved_license() -> None:
    constraint_names = {constraint.name for constraint in MemberImageCandidate.__table__.constraints}

    assert "ck_member_image_candidate_approved_license" in constraint_names
    assert "uq_member_approved_image" in {index.name for index in MemberImageCandidate.__table__.indexes}


def test_source_identifier_requires_a_review_status_and_is_unique_per_source() -> None:
    constraint_names = {constraint.name for constraint in MemberSourceIdentifier.__table__.constraints}

    assert "ck_member_source_identifier_status" in constraint_names
    assert "uq_member_source_identifier" in constraint_names
    assert "uq_member_source_identifier_evidence" in {constraint.name for constraint in MemberSourceIdentifierEvidence.__table__.constraints}