from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from backend.app.schemas.profile import ProfileUpdate, ProfileResponse
from backend.app.services.profile_service import profile_service
from backend.app.api.deps import get_current_citizen_id

router = APIRouter(prefix="/profiles", tags=["Profile"])


@router.get("/me", response_model=ProfileResponse)
async def get_my_profile(citizen_id: Optional[str] = Depends(get_current_citizen_id)):
    """
    Retrieve the current authenticated user's profile.
    Requires authentication; returns the citizen's authentic profile.
    """
    if not citizen_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials required. Please sign in."
        )
    return profile_service.get_profile(citizen_id)


@router.put("/me", response_model=ProfileResponse)
async def update_my_profile(
    profile_in: ProfileUpdate,
    citizen_id: Optional[str] = Depends(get_current_citizen_id)
):
    """Create or update current authenticated user's profile."""
    if not citizen_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials required. Please sign in."
        )
    return profile_service.update_profile(profile_in, citizen_id)
