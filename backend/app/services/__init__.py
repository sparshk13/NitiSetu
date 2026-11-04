"""
Services package initialization.
Exposes core business logic singletons across NitiSetu.
"""
from backend.app.services.scheme_service import scheme_service
from backend.app.services.rag_service import rag_service
from backend.app.services.eligibility_engine import eligibility_engine
from backend.app.services.document_service import document_service
from backend.app.services.profile_service import profile_service
from backend.app.services.application_service import application_service
from backend.app.services.auth_service import auth_service

__all__ = [
    "scheme_service",
    "rag_service",
    "eligibility_engine",
    "document_service",
    "profile_service",
    "application_service",
    "auth_service"
]
