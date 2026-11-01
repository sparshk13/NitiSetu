from typing import List, Optional
from pydantic import BaseModel, Field


class SchemeListItem(BaseModel):
    id: str
    slug: str
    name: str
    summary: Optional[str] = None
    level: str = Field("Central Government", description="Central or State government")
    state_or_ministry: Optional[str] = None
    scheme_type: str = "scholarship"
    application_mode: Optional[str] = "Online"
    benefit_summary: Optional[str] = None
    official_url: str
    last_verified_at: str
    recommendation_reason: Optional[str] = None


class SchemeListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[SchemeListItem]


class SchemeDetailResponse(BaseModel):
    id: str
    slug: str
    name: str
    summary: Optional[str] = None
    description: Optional[str] = None
    level: str
    state_or_ministry: Optional[str] = None
    scheme_type: str
    application_mode: Optional[str] = None
    benefit_summary: Optional[str] = None
    eligibility_criteria_text: Optional[str] = None
    exclusions_text: Optional[str] = None
    application_process_text: Optional[str] = None
    documents_required_text: Optional[str] = None
    detected_document_tags: List[str] = []
    faqs: Optional[str] = None
    official_url: str
    application_url: Optional[str] = None
    last_verified_at: str
    source_provenance: str = "myScheme.gov.in (Official Government of India Registry)"


class SchemeRecommendationRequest(BaseModel):
    state_code: Optional[str] = None
    occupation: Optional[str] = None
    age: Optional[int] = None
    education_level: Optional[str] = None
    caste_category: Optional[str] = None
    annual_family_income: Optional[float] = None
    ration_card_type: Optional[str] = None
    is_landowner: Optional[bool] = False
    highest_qualification: Optional[str] = None
    gender: Optional[str] = None
    is_differently_abled: Optional[bool] = False
    limit: int = 10

