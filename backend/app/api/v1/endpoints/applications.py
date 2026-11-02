from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends
from backend.app.schemas.application import (
    ApplicationDraftCreate,
    ApplicationDraftResponse,
    DemoPrepareRequest
)
from backend.app.services.application_service import application_service
from backend.app.api.deps import get_current_citizen_id

router = APIRouter(prefix="/applications", tags=["Applications"])


@router.get("/drafts", response_model=List[ApplicationDraftResponse])
async def list_drafts(citizen_id: Optional[str] = Depends(get_current_citizen_id)):
    """List current authenticated citizen's prepared application drafts."""
    return application_service.list_drafts(user_id=citizen_id)


@router.post("/drafts", response_model=ApplicationDraftResponse)
async def create_draft(
    request: ApplicationDraftCreate,
    citizen_id: Optional[str] = Depends(get_current_citizen_id)
):
    """Prepare a pre-filled application draft from verified profile facts of the current citizen."""
    return application_service.create_draft(request, user_id=citizen_id)



@router.post("/drafts/{draft_id}/prepare-demo", response_model=ApplicationDraftResponse)
async def prepare_demo(
    draft_id: str, 
    request: DemoPrepareRequest,
    citizen_id: Optional[str] = Depends(get_current_citizen_id)
):
    """
    Demonstrate automated form filling against a controlled, isolated demo portal.
    Requires explicit citizen confirmation. Never submits live applications.
    """
    if not request.confirmed_by_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Explicit user confirmation is required before initiating demo form filling."
        )

    result = application_service.prepare_demo(draft_id, user_id=citizen_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Draft not found or unauthorized.")
    return result

