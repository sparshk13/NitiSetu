import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional
from backend.app.schemas.application import (
    ApplicationDraftCreate,
    ApplicationDraftResponse,
    ApplicationDraftUpdate
)
from backend.app.services.scheme_service import scheme_service
from backend.app.services.profile_service import profile_service

_DRAFTS_STORE: Dict[str, Dict] = {}


class ApplicationService:
    def __init__(self):
        # Pre-seed default draft
        self._seed_default_draft()

    def _seed_default_draft(self):
        draft_id = "draft-seed-nsp-01"
        _DRAFTS_STORE[draft_id] = {
            "id": draft_id,
            "user_id": "00000000-0000-0000-0000-000000000001",
            "scheme_id": "national-scholarship-post-matric",
            "scheme_name": "Post-Matric Scholarship Scheme for SC/ST/OBC/Minorities",
            "status": "ready_for_review",
            "form_data": {
                "applicant_name": "Aarav Sharma",
                "domicile_state": "Gujarat",
                "institution_name": "Gujarat Technological University",
                "course_name": "B.Tech Computer Engineering",
                "study_year": 2,
                "annual_family_income": 220000.0,
                "caste_category": "OBC",
                "bank_aadhaar_seeded": True
            },
            "automation_log": None,
            "created_at": "2024-10-30T09:00:00Z",
            "updated_at": "2024-10-30T09:00:00Z"
        }

    def list_drafts(self, user_id: Optional[str] = None) -> List[ApplicationDraftResponse]:
        target_uid = user_id or "00000000-0000-0000-0000-000000000001"
        results = []
        for d in _DRAFTS_STORE.values():
            if d.get("user_id") == target_uid:
                results.append(ApplicationDraftResponse(
                    id=d["id"],
                    user_id=d["user_id"],
                    scheme_id=d["scheme_id"],
                    scheme_name=d["scheme_name"],
                    status=d["status"],
                    form_data=d["form_data"],
                    automation_log=d.get("automation_log"),
                    created_at=d["created_at"],
                    updated_at=d["updated_at"]
                ))
        return results

    def create_draft(self, draft_in: ApplicationDraftCreate, user_id: Optional[str] = None) -> ApplicationDraftResponse:
        target_uid = user_id or "00000000-0000-0000-0000-000000000001"
        
        # Check if an existing draft already exists for this citizen and scheme
        for existing in _DRAFTS_STORE.values():
            if existing.get("user_id") == target_uid and existing.get("scheme_id") == draft_in.scheme_id:
                if draft_in.form_data:
                    existing["form_data"].update(draft_in.form_data)
                    existing["updated_at"] = datetime.now(timezone.utc).isoformat()
                return ApplicationDraftResponse(**existing)

        draft_id = str(uuid.uuid4())
        scheme = scheme_service.get_scheme_by_slug(draft_in.scheme_id)
        scheme_name = scheme.name if scheme else draft_in.scheme_id

        # Merge actual requesting citizen's profile facts
        profile = profile_service.get_profile(target_uid).model_dump()
        form_data = {
            "applicant_name": profile.get("full_name"),
            "domicile_state": profile.get("state_code"),
            "institution_name": profile.get("institution_name"),
            "course_name": profile.get("course"),
            "study_year": profile.get("study_year"),
            "annual_family_income": profile.get("annual_family_income"),
            "caste_category": profile.get("caste_category"),
        }
        form_data.update(draft_in.form_data or {})

        now_str = datetime.now(timezone.utc).isoformat()
        draft = {
            "id": draft_id,
            "user_id": target_uid,
            "scheme_id": draft_in.scheme_id,
            "scheme_name": scheme_name,
            "status": "ready_for_review",
            "form_data": form_data,
            "automation_log": None,
            "created_at": now_str,
            "updated_at": now_str
        }

        _DRAFTS_STORE[draft_id] = draft
        return ApplicationDraftResponse(**draft)


    def prepare_demo(self, draft_id: str, user_id: Optional[str] = None) -> Optional[ApplicationDraftResponse]:
        draft = _DRAFTS_STORE.get(draft_id)
        if not draft:
            return None

        # Ownership guardrail
        if user_id and draft.get("user_id") != user_id and draft.get("user_id") != "00000000-0000-0000-0000-000000000001":
            return None

        # Execute safe demo simulation with strict guardrails
        logs = [
            "Initializing isolated demo portal sandbox...",
            f"Pre-populating student facts for: {draft['form_data'].get('applicant_name')}...",
            f"Mapped AISHE Code & Course: {draft['form_data'].get('course_name')}...",
            f"Verified Means Threshold: ₹ {draft['form_data'].get('annual_family_income')}...",
            "Controlled Demo: Application fields successfully filled.",
            "SAFETY GUARDRAIL: Final submission aborted. Application prepared for manual citizen review."
        ]

        draft["status"] = "demo_completed"
        draft["automation_log"] = logs
        draft["updated_at"] = datetime.now(timezone.utc).isoformat()
        _DRAFTS_STORE[draft_id] = draft

        return ApplicationDraftResponse(**draft)


application_service = ApplicationService()
