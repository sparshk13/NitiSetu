from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, Depends
from backend.app.schemas.document import DocumentResponse, DocumentExtractionConfirmRequest, DocumentChecklistResponse
from backend.app.services.document_service import document_service
from backend.app.api.deps import get_current_citizen_id

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.get("", response_model=List[DocumentResponse])
async def list_documents(citizen_id: Optional[str] = Depends(get_current_citizen_id)):
    """List documents for the current authenticated user only."""
    return document_service.list_documents(user_id=citizen_id)


@router.post("", response_model=DocumentResponse)
@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    document_type: Optional[str] = Form(None),
    citizen_id: Optional[str] = Depends(get_current_citizen_id)
):
    """
    Secure document upload with template verification and tailored fact extraction.
    Rejects corrupted or non-governmental files with a verification failure explanation.
    """
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds maximum allowed limit of 10 MB."
        )

    # Basic extension validation
    allowed_exts = {".pdf", ".png", ".jpg", ".jpeg"}
    ext = "." + file.filename.split(".")[-1].lower() if "." in file.filename else ""
    if ext not in allowed_exts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{ext}'. Allowed types: PDF, PNG, JPG, JPEG."
        )

    return document_service.simulate_or_parse_upload(
        filename=file.filename,
        content_bytes=content,
        user_id=citizen_id,
        expected_type=document_type
    )


@router.post("/{doc_id}/confirm", response_model=DocumentResponse)
@router.post("/{doc_id}/confirm-extraction", response_model=DocumentResponse)
async def confirm_extraction(doc_id: str, request: DocumentExtractionConfirmRequest):
    """Citizen confirms or edits extracted document facts before saving to vault."""
    result = document_service.confirm_extraction(doc_id, request.confirmed_fields)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
    return result


@router.delete("/{doc_id}")
async def delete_document(
    doc_id: str,
    citizen_id: Optional[str] = Depends(get_current_citizen_id)
):
    """Delete a document from citizen vault."""
    success = document_service.delete_document(doc_id, user_id=citizen_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
    return {"message": "Document deleted successfully", "id": doc_id}


@router.get("/checklist/{scheme_slug}", response_model=DocumentChecklistResponse)
async def get_scheme_document_checklist(scheme_slug: str):
    """Compare user's verified document vault against authentic scheme requirements."""
    return document_service.get_scheme_checklist(scheme_slug)
