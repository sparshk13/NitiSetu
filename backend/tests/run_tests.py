import sys
import unittest
from pathlib import Path

# Ensure project root is in sys.path
root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root))

from backend.app.services.eligibility_engine import eligibility_engine
from backend.app.schemas.eligibility import EligibilityStatusEnum
from backend.app.services.scheme_service import scheme_service
from backend.app.schemas.scheme import SchemeRecommendationRequest
from backend.app.services.rag_service import rag_service
from backend.app.schemas.assistant import AssistantQueryRequest
from backend.app.services.document_service import document_service
from backend.app.services.application_service import application_service
from backend.app.schemas.application import ApplicationDraftCreate


class TestNitiSetuCore(unittest.TestCase):
    def test_document_extraction_and_confirmation(self):
        """Document parsing requires human confirmation before status becomes verified."""
        upload_resp = document_service.simulate_or_parse_upload(
            "Income_Certificate_Tehsildar.pdf", b"%PDF-1.4 sample content"
        )
        self.assertEqual(upload_resp.processing_status, "awaiting_user_confirmation")
        self.assertIsNotNone(upload_resp.extracted_fields)

        # Confirm extraction
        confirmed = document_service.confirm_extraction(upload_resp.id, {"annual_family_income": 220000.0})
        self.assertEqual(confirmed.processing_status, "verified")
        self.assertEqual(confirmed.user_confirmed_fields["annual_family_income"], 220000.0)

    def test_application_draft_and_controlled_demo(self):
        """Application draft populates profile facts and demo enforces stop-before-submit."""
        draft = application_service.create_draft(ApplicationDraftCreate(
            scheme_id="national-scholarship-post-matric",
            form_data={"course_name": "B.Tech Computer Science"}
        ))
        self.assertEqual(draft.status, "ready_for_review")
        self.assertIn("Aarav", draft.form_data["applicant_name"])

        # Run controlled demo
        demo_resp = application_service.prepare_demo(draft.id)
        self.assertEqual(demo_resp.status, "demo_completed")
        self.assertTrue(any("SAFETY GUARDRAIL" in log for log in demo_resp.automation_log))

    def test_rag_grounded_answer_with_citations(self):

        """Querying scholarship income limit returns cited official guidelines."""
        req = AssistantQueryRequest(
            scheme_id="national-scholarship-post-matric",
            question="What is the family income limit for the scholarship?"
        )
        resp = rag_service.answer_query(req)
        self.assertFalse(resp.insufficient_evidence)
        self.assertGreater(len(resp.citations), 0)
        self.assertIn("scholarship", resp.citations[0].source_title.lower())
        self.assertTrue("2,50,000" in resp.answer or "4,50,000" in resp.answer or "income" in resp.answer.lower())

    def test_rag_insufficient_evidence_handling(self):
        """Unrelated or ungrounded questions safely return insufficient_evidence=True."""
        req = AssistantQueryRequest(
            scheme_id="national-scholarship-post-matric",
            question="What is the ticket price for Disneyland Paris in Euros?"
        )
        resp = rag_service.answer_query(req)
        self.assertTrue(resp.insufficient_evidence)
        self.assertEqual(len(resp.citations), 0)

    def test_scheme_catalog_loaded(self):

        """Verify 2,066 authentic schemes are loaded."""
        self.assertGreater(len(scheme_service._schemes), 2000)
        res = scheme_service.list_schemes(page=1, page_size=10)
        self.assertGreater(res.total, 2000)
        self.assertEqual(len(res.items), 10)

    def test_scheme_search_query(self):
        """Searching for 'scholarship' yields relevant results."""
        res = scheme_service.list_schemes(q="scholarship", page_size=5)
        self.assertGreater(res.total, 0)
        for item in res.items:
            scheme_full = scheme_service.get_scheme_by_slug(item.slug)
            text = f"{scheme_full.name} {scheme_full.description} {scheme_full.benefit_summary}".lower()
            self.assertTrue(
                "scholarship" in text or "student" in text or "fellowship" in text or "education" in text,
                f"Unexpected scheme without student keywords: {item.name}"
            )


    def test_scheme_recommendations(self):
        """Recommendations return plain-language match reasons."""
        req = SchemeRecommendationRequest(
            state_code="Gujarat",
            education_level="Undergraduate",
            caste_category="OBC",
            annual_family_income=200000.0,
            gender="Male",
            limit=5
        )
        recs = scheme_service.get_recommendations(req)
        self.assertGreater(len(recs), 0)
        for r in recs:
            self.assertIsNotNone(r.recommendation_reason)
            self.assertGreater(len(r.recommendation_reason), 5)

    def test_national_scholarship_eligible(self):
        """Eligible OBC student with low income passes deterministically."""
        profile = {
            "annual_family_income": 200000.0,
            "caste_category": "OBC",
            "education_level": "Undergraduate",
            "student_status": "Student"
        }
        result = eligibility_engine.evaluate("national-scholarship-post-matric", profile)
        self.assertEqual(result.status, EligibilityStatusEnum.POTENTIALLY_ELIGIBLE)
        self.assertGreaterEqual(len(result.matched_rules), 3)
        self.assertEqual(len(result.failed_rules), 0)
        self.assertEqual(len(result.missing_fields), 0)

    def test_national_scholarship_income_exceeded(self):
        """Income exceeding cap fails deterministically."""
        profile = {
            "annual_family_income": 350000.0,
            "caste_category": "OBC",
            "education_level": "Undergraduate",
            "student_status": "Student"
        }
        result = eligibility_engine.evaluate("national-scholarship-post-matric", profile)
        self.assertEqual(result.status, EligibilityStatusEnum.NOT_ELIGIBLE)
        self.assertTrue(any(r.rule_key == "annual_family_income" and r.passed is False for r in result.failed_rules))

    def test_national_scholarship_caste_mismatch(self):
        """General category applying for reserved scheme fails deterministically."""
        profile = {
            "annual_family_income": 150000.0,
            "caste_category": "General",
            "education_level": "Undergraduate",
            "student_status": "Student"
        }
        result = eligibility_engine.evaluate("national-scholarship-post-matric", profile)
        self.assertEqual(result.status, EligibilityStatusEnum.NOT_ELIGIBLE)
        self.assertTrue(any(r.rule_key == "caste_category" and r.passed is False for r in result.failed_rules))

    def test_national_scholarship_missing_income(self):
        """Missing income results in needs_information, never assumed 0."""
        profile = {
            "annual_family_income": None,
            "caste_category": "SC",
            "education_level": "Undergraduate",
            "student_status": "Student"
        }
        result = eligibility_engine.evaluate("national-scholarship-post-matric", profile)
        self.assertEqual(result.status, EligibilityStatusEnum.NEEDS_INFORMATION)
        self.assertIn("annual_family_income", result.missing_fields)


if __name__ == "__main__":
    unittest.main(verbosity=2)
