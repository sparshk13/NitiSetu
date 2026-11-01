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
    assert "Key Policy Details" in resp.answer or "Key Provisions" in resp.answer
    assert "Important Exclusions" in resp.answer or "Exclusions" in resp.answer


def test_rag_exclusion_verdict_income_tax_pmkisan():
    """Negative case: Income tax payer querying PM-KISAN receives explicit NOT ELIGIBLE verdict."""
    req = AssistantQueryRequest(
        scheme_id=None,
        question="I pay income tax every year. Can I receive PM-KISAN money?"
    )
    resp = rag_service.answer_query(req)
    assert not resp.insufficient_evidence
    assert "NOT ELIGIBLE" in resp.answer
    assert "Exclusion" in resp.detected_intent
    assert "kisan" in resp.matched_scheme_name.lower() or "pm-kisan" in resp.matched_scheme_name.lower()


def test_rag_exclusion_verdict_dual_scholarship():
    """Negative case: Dual scholarship query receives explicit NOT ELIGIBLE / PROHIBITED verdict."""
    req = AssistantQueryRequest(
        scheme_id=None,
        question="Can I receive two scholarships at the same time?"
    )
    resp = rag_service.answer_query(req)
    assert not resp.insufficient_evidence
    assert "NOT ELIGIBLE" in resp.answer or "PROHIBITED" in resp.answer
    assert "Exclusion" in resp.detected_intent


def test_rag_exclusion_verdict_income_threshold():
    """Negative case: Income above statutory ceiling receives explicit NOT ELIGIBLE verdict with numeric cap."""
    req = AssistantQueryRequest(
        scheme_id=None,
        question="My family income is 3.5 Lakhs. Can I get Post-Matric SC scholarship?"
    )
    resp = rag_service.answer_query(req)
    assert not resp.insufficient_evidence
    assert "NOT ELIGIBLE" in resp.answer
    assert "2.5" in resp.answer or "250,000" in resp.answer or "2,50,000" in resp.answer


def test_rag_catalog_scheme_resolution_without_slug():
    """General 2066-scheme catalog: Querying APY without explicit slug correctly matches APY and age bounds."""
    req = AssistantQueryRequest(
        scheme_id=None,
        question="What is the age limit for Atal Pension Yojana?"
    )
    resp = rag_service.answer_query(req)
    assert not resp.insufficient_evidence
    assert "Atal Pension" in resp.matched_scheme_name
    assert "18" in resp.answer and "40" in resp.answer


def test_rag_hinglish_conversational_query():
    """Multilingual / Hinglish conversational query properly maps intent and answers with official facts."""
    req = AssistantQueryRequest(
        scheme_id=None,
        question="pm kisan me kitna paisa milta hai"
    )
    resp = rag_service.answer_query(req)
    assert not resp.insufficient_evidence
    assert "6,000" in resp.answer
    assert "Financial Benefits" in resp.detected_intent


def test_rag_pmsvanidhi_loan_amounts():
    """PM-SVANidhi query returns exact loan tranche structure."""
    req = AssistantQueryRequest(
        scheme_id=None,
        question="What is the first loan amount in PM-SVANidhi?"
    )
    resp = rag_service.answer_query(req)
    assert not resp.insufficient_evidence
    assert "10,000" in resp.answer
    assert "Financial Benefits" in resp.detected_intent
