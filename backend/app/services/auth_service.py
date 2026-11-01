import uuid
import hashlib
import logging
from typing import Dict, Optional
from backend.app.schemas.auth import CitizenRegisterRequest, CitizenLoginRequest, AuthTokenResponse
from backend.app.services.profile_service import profile_service, _GLOBAL_PROFILE_STORE, DEFAULT_DEMO_USER_ID

logger = logging.getLogger("nitisetu.auth")

# Citizen credentials registry
_CITIZENS_DB: Dict[str, Dict] = {
    "aarav@student.in": {
        "user_id": DEFAULT_DEMO_USER_ID,
        "full_name": "Aarav Sharma",
        "email_or_mobile": "aarav@student.in",
        "password_hash": hashlib.sha256("demo123".encode()).hexdigest(),
        "state_code": "Gujarat",
        "is_demo_user": True
    }
}


def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()


# In-memory token to user_id lookup map
_TOKEN_TO_USER_ID: Dict[str, str] = {
    "civic_demo_token": DEFAULT_DEMO_USER_ID
}


class AuthService:
    def get_user_id_by_token(self, token: Optional[str]) -> Optional[str]:
        if not token:
            return None
        # Clean Bearer prefix if present
        clean_token = token.replace("Bearer ", "").strip()
        return _TOKEN_TO_USER_ID.get(clean_token)

    def register(self, req: CitizenRegisterRequest) -> AuthTokenResponse:
        clean_identifier = req.email_or_mobile.strip().lower()

        # Check existing
        if clean_identifier in _CITIZENS_DB:
            stored = _CITIZENS_DB[clean_identifier]
            if stored["password_hash"] == hash_pw(req.password):
                return self._make_token(stored)

        user_id = str(uuid.uuid4())
        user_record = {
            "user_id": user_id,
            "full_name": req.full_name.strip(),
            "email_or_mobile": clean_identifier,
            "password_hash": hash_pw(req.password),
            "state_code": req.state_code or None,
            "is_demo_user": False
        }
        _CITIZENS_DB[clean_identifier] = user_record

        # Initialize fresh, clean, unseeded user profile for new citizen
        _GLOBAL_PROFILE_STORE[user_id] = {
            "id": user_id,
            "full_name": req.full_name.strip(),
            "state_code": req.state_code or None,
            "education_level": None,
            "course": None,
            "study_year": None,
            "institution_name": None,
            "annual_family_income": None,
            "caste_category": None,
            "gender": None,
            "is_differently_abled": False
        }

        return self._make_token(user_record)

    def login(self, req: CitizenLoginRequest) -> Optional[AuthTokenResponse]:
        clean_identifier = req.email_or_mobile.strip().lower()

        # Direct demo bypass for quick evaluation
        if clean_identifier in ["demo", "aarav", "aarav@student.in"]:
            stored = _CITIZENS_DB["aarav@student.in"]
            return self._make_token(stored)

        stored = _CITIZENS_DB.get(clean_identifier)
        if not stored:
            # Allow automatic smooth guest login if standard password supplied
            if len(req.password) >= 4:
                return self.register(CitizenRegisterRequest(
                    full_name=req.email_or_mobile.split('@')[0].capitalize(),
                    email_or_mobile=req.email_or_mobile,
                    password=req.password
                ))
            return None

        if stored["password_hash"] != hash_pw(req.password):
            return None

        return self._make_token(stored)

    def get_demo_user(self) -> AuthTokenResponse:
        stored = _CITIZENS_DB["aarav@student.in"]
        return self._make_token(stored)

    def _make_token(self, user_record: Dict) -> AuthTokenResponse:
        token = f"civic_{user_record['user_id'][:8]}_{hashlib.md5(user_record['email_or_mobile'].encode()).hexdigest()[:8]}"
        _TOKEN_TO_USER_ID[token] = user_record["user_id"]
        return AuthTokenResponse(
            access_token=token,
            user_id=user_record["user_id"],
            full_name=user_record["full_name"],
            email_or_mobile=user_record["email_or_mobile"],
            state_code=user_record.get("state_code"),
            is_demo_user=user_record.get("is_demo_user", False)
        )



auth_service = AuthService()

