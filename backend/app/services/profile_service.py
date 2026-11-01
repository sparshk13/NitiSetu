import logging
from typing import Dict, Optional
from backend.app.schemas.profile import ProfileCreate, ProfileUpdate, ProfileResponse

logger = logging.getLogger("civicpilot.profile")

# In-memory / session profile cache for rapid prototyping, synced with DB
_GLOBAL_PROFILE_STORE: Dict[str, Dict] = {}

DEFAULT_DEMO_USER_ID = "00000000-0000-0000-0000-000000000001"


class ProfileService:
    def __init__(self):
        # Demo persona
        _GLOBAL_PROFILE_STORE[DEFAULT_DEMO_USER_ID] = {
            "id": DEFAULT_DEMO_USER_ID,
            "full_name": "Aarav Sharma",
            "age": 20,
            "gender": "Male",
            "marital_status": "Single",
            "state_code": "Gujarat",
            "district": "Ahmedabad",
            "area_type": "Urban",
            "occupation": "Student / Scholar",
            "annual_family_income": 220000.0,
            "ration_card_type": "BPL / Priority Household (PHH)",
            "caste_category": "OBC",
            "is_minority_community": False,
            "is_differently_abled": False,
            "is_landowner": False,
            "land_holding_acres": 0.0,
            "has_bank_account": True,
            "is_bank_aadhaar_seeded": True,
            "highest_qualification": "12th Passed",
            "is_student_currently": True,
            "education_level": "Undergraduate",
            "course": "Bachelor of Technology (Computer Science)",
            "study_year": 2,
            "institution_name": "Gujarat Technological University"
        }

    def _calculate_completeness(self, data: Dict) -> int:
        """Calculate percentage of filled essential fields tailored to the citizen's profile."""
        core_fields = ["full_name", "state_code", "occupation", "annual_family_income", "caste_category", "gender"]
        
        occ = str(data.get("occupation") or "").lower()
        if "student" in occ or data.get("is_student_currently"):
            core_fields.extend(["course", "institution_name", "education_level"])
        elif "farmer" in occ:
            core_fields.extend(["is_landowner", "land_holding_acres"])
        else:
            core_fields.append("highest_qualification")

        filled = sum(1 for f in core_fields if data.get(f) is not None and str(data.get(f)).strip() != "")
        return int((filled / len(core_fields)) * 100)

    def get_profile(self, user_id: Optional[str] = None) -> ProfileResponse:
        """Get profile for a specific user. Never defaults a registered citizen to demo data."""
        target_id = user_id or DEFAULT_DEMO_USER_ID
        data = _GLOBAL_PROFILE_STORE.get(target_id)
        if not data:
            # Clean, unseeded blank profile for new citizen
            data = {
                "id": target_id,
                "full_name": None,
                "age": None,
                "gender": None,
                "marital_status": None,
                "state_code": None,
                "district": None,
                "area_type": "Rural",
                "occupation": None,
                "annual_family_income": None,
                "ration_card_type": None,
                "caste_category": None,
                "is_minority_community": False,
                "is_differently_abled": False,
                "is_landowner": False,
                "land_holding_acres": None,
                "has_bank_account": True,
                "is_bank_aadhaar_seeded": True,
                "highest_qualification": None,
                "is_student_currently": False,
                "education_level": None,
                "course": None,
                "study_year": None,
                "institution_name": None
            }
            _GLOBAL_PROFILE_STORE[target_id] = data

        completeness = self._calculate_completeness(data)
        return ProfileResponse(**data, completeness_percentage=completeness)

    def update_profile(self, profile_update: ProfileUpdate, user_id: Optional[str] = None) -> ProfileResponse:
        """Update profile for a specific user."""
        target_id = user_id or DEFAULT_DEMO_USER_ID
        current = _GLOBAL_PROFILE_STORE.get(target_id, {"id": target_id})
        update_dict = profile_update.model_dump(exclude_unset=True)
        current.update(update_dict)
        _GLOBAL_PROFILE_STORE[target_id] = current

        completeness = self._calculate_completeness(current)
        return ProfileResponse(**current, completeness_percentage=completeness)


profile_service = ProfileService()
