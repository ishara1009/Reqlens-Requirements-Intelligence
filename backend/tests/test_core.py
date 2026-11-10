from app.audit import audit_chunks
from app.ingestion import chunk_pages
from app.rag import compress_for_generation, cosine, expand_queries, parse_metadata_filters
from app.services import finding_key


def chunk(chunk_id: str, text: str, document_id: str = "d1"):
    return {"chunk_id": chunk_id, "document_id": document_id, "filename": "SRS.txt", "text": text, "page_number": 1, "section": None, "score": None}


def test_requirement_chunking_preserves_text():
    result = chunk_pages([(1, "REQ-AUTH-1: Users must log in.\nREQ-AUTH-2: Sessions expire after 30 minutes.")])
    assert len(result) == 2
    assert result[0]["page_number"] == 1


def test_audit_detects_ambiguity_and_conflicting_duration():
    rows = audit_chunks("p1", [chunk("c1", "The session must expire after 30 minutes and be user-friendly."), chunk("c2", "The session must expire after 24 hours.", "d2")])
    assert {row["issue_type"] for row in rows} >= {"ambiguity", "contradiction"}


def test_cosine_similarity():
    assert cosine([1, 0], [1, 0]) == 1
    assert cosine([1, 0], [0, 1]) == 0


def test_advanced_retrieval_helpers_are_bounded_and_safe():
    assert expand_queries("Explain REQ-AUTH-104") == ["Explain REQ-AUTH-104"]
    assert len(expand_queries("login security problems")) <= 4
    assert parse_metadata_filters("Security Policy version 2") == {"version": "2", "document_type": "Security Policy"}
    assert "$where" not in parse_metadata_filters("version 2 $where")
    assert len(compress_for_generation("session timeout", "Unrelated sentence. Session timeout is 30 minutes.")) <= 700


def test_finding_key_deduplicates_the_same_issue_regardless_of_evidence_order():
    left = {"issue_type": "contradiction", "evidence": [{"chunk_id": "c2"}, {"chunk_id": "c1"}]}
    right = {"issue_type": "contradiction", "evidence": [{"chunk_id": "c1"}, {"chunk_id": "c2"}]}
    assert finding_key(left) == finding_key(right)

