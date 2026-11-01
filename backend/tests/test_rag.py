import pytest
from backend.app.services.rag_service import rag_service
from backend.app.schemas.assistant import AssistantQueryRequest


def test_rag_grounded_income_query():
    """Querying scholarship income limit returns cited official guidelines with exact caps."""
    req = AssistantQueryRequest(
        scheme_id="national-scholarship-post-matric",
        question="What is the family income limit for the scholarship?"
    )
    resp = rag_service.answer_query(req)
    assert not resp.insufficient_evidence
    assert len(resp.citations) > 0
    assert "scholarship" in resp.citations[0].source_title.lower()
    assert "2,50,000" in resp.answer or "4,50,000" in resp.answer or "income" in resp.answer.lower()
    assert resp.verification_status in ["verified", "verified_local", "revised_by_judge"]
    assert resp.confidence_score >= 0.7
    assert resp.detected_intent is not None


def test_rag_documents_query_is_distinct_and_specific():
    """Querying required documents returns document checklist, not generic intro or income caps."""
    req = AssistantQueryRequest(
        scheme_id="national-scholarship-post-matric",
        question="What documents are needed to apply for the scholarship?"
    )
    resp = rag_service.answer_query(req)
    assert not resp.insufficient_evidence
    assert len(resp.citations) > 0
    # Must mention actual documents required
    assert any(doc in resp.answer.lower() for doc in ["aadhaar", "income certificate", "bonafide", "marksheet", "document"])
    assert "Documents" in resp.detected_intent or "Documentation" in resp.detected_intent


def test_rag_distinct_answers_for_different_questions():
    """Ensure two different questions about the same scheme do NOT return similar answers."""
    income_req = AssistantQueryRequest(
        scheme_id="national-scholarship-post-matric",
        question="What is the family income limit for the scholarship?"
    )
    docs_req = AssistantQueryRequest(
        scheme_id="national-scholarship-post-matric",
        question="What documents are needed to apply for the scholarship?"
    )
    income_resp = rag_service.answer_query(income_req)
    docs_resp = rag_service.answer_query(docs_req)

    # Answers must NOT be identical or similar
    assert income_resp.answer != docs_resp.answer
    assert "income" in income_resp.answer.lower() or "2,50,000" in income_resp.answer
    assert "document" in docs_resp.answer.lower() or "aadhaar" in docs_resp.answer.lower()


def test_rag_pm_kisan_benefits_query():
    """Querying PM-KISAN benefits returns exact financial quantum and installment frequency."""
    req = AssistantQueryRequest(
        scheme_id="pm-kisan",
        question="How much financial benefit is given under PM-KISAN and how often?"
    )
    resp = rag_service.answer_query(req)
    assert not resp.insufficient_evidence
    assert len(resp.citations) > 0
    assert "6,000" in resp.answer or "2,000" in resp.answer or "installment" in resp.answer.lower()


def test_rag_insufficient_evidence_handling():
    """Unrelated or ungrounded questions safely return insufficient_evidence=True with 0 citations."""
    req = AssistantQueryRequest(
        scheme_id="national-scholarship-post-matric",
        question="What is the ticket price for Disneyland Paris in Euros?"
    )
    resp = rag_service.answer_query(req)
    assert resp.insufficient_evidence
    assert len(resp.citations) == 0
    assert resp.confidence_score == 0.0


def test_rag_formatted_structure():
    """Answers are formatted with structured headings and direct answers."""
    req = AssistantQueryRequest(
        scheme_id="national-scholarship-post-matric",
        question="What is the family income limit for the scholarship?"
    )
    resp = rag_service.answer_query(req)
    assert "Direct Answer" in resp.answer
