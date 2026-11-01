from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class DocumentExtractionConfirmRequest(BaseModel):
    confirmed_fields: Dict[str, Any] = Field(..., description="User-confirmed or corrected key-value fields")


class DocumentResponse(BaseModel):
    id: str
    original_filename: str
    file_size: int
    detected_type: Optional[str] = None
    processing_status: str  # 'verified', 'awaiting_user_confirmation', 'rejected_unrecognized'
    is_valid: bool = True
    verification_score: Optional[int] = 95
    verification_error: Optional[str] = None
    issuing_authority: Optional[str] = None
    tag: Optional[str] = None
    extracted_fields: Optional[Dict[str, Any]] = None
    user_confirmed_fields: Optional[Dict[str, Any]] = None
    created_at: str


class DocumentChecklistResponse(BaseModel):
    scheme_id: str
    required_document_tags: List[str]
    uploaded_document_tags: List[str]
    missing_document_tags: List[str]
    is_ready_for_application: bool
