from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from backend.app.schemas.scheme import (
    SchemeListItem,
    SchemeListResponse,
    SchemeDetailResponse,
    SchemeRecommendationRequest
)
from backend.app.services.scheme_service import scheme_service

router = APIRouter(prefix="/schemes", tags=["Schemes"])


@router.get("", response_model=SchemeListResponse)
async def list_schemes(
    q: Optional[str] = Query(None, description="Search keyword across name, description, tags, and ministry"),
    state: Optional[str] = Query(None, description="Filter by state or UT"),
    level: Optional[str] = Query(None, description="Central Government or State Government"),
    scheme_type: Optional[str] = Query(None, description="Scheme type filter (default: None for all welfare sectors)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(12, ge=1, le=100, description="Items per page")
):
    """
    Search and filter authentic government schemes from the 2,066 master repository across all welfare sectors.
    """
    return scheme_service.list_schemes(
        q=q,
        state=state,
        level=level,
        scheme_type=scheme_type,
        page=page,
        page_size=page_size
    )


@router.get("/{scheme_slug}", response_model=SchemeDetailResponse)
async def get_scheme_detail(scheme_slug: str):
    """
    Fetch comprehensive authentic details for a specific scheme by slug.
    Includes verified benefits, eligibility criteria, required documents, and official URLs.
    """
    scheme = scheme_service.get_scheme_by_slug(scheme_slug)
    if not scheme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scheme with slug '{scheme_slug}' not found in government registry."
        )
    return scheme


@router.post("/recommendations", response_model=List[SchemeListItem])
async def recommend_schemes(request: SchemeRecommendationRequest):
    """
    Recommend relevant government schemes and scholarships based on user demographic,
    educational, and economic facts. Provides plain-language justification for each recommendation.
    """
    return scheme_service.get_recommendations(request)

