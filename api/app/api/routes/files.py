from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.core.constants import SUPPORTED_SUFFIXES
from app.schemas.files import FileStatusResponse, FileUploadResponse
from app.services.local_file_storage import (
    get_file_status as get_stored_file_status,
)
from app.services.local_file_storage import save_uploaded_file

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    *,
    workspace_id: str = Form(...),
    uploaded_file: UploadFile = File(...),
) -> FileUploadResponse:
    if not (uploaded_file.filename or "").strip():
        raise HTTPException(status_code=400, detail="filename_required")
    if Path(uploaded_file.filename).suffix.lower() not in SUPPORTED_SUFFIXES:
        raise HTTPException(status_code=400, detail="unsupported_file_type")

    stored_file = await save_uploaded_file(
        workspace_id=workspace_id,
        uploaded_file=uploaded_file,
    )
    return FileUploadResponse(file_id=stored_file.file_id, status=stored_file.status)


@router.get("/{file_id}/status", response_model=FileStatusResponse)
def get_file_status(*, file_id: str) -> FileStatusResponse:
    status = get_stored_file_status(file_id=file_id)
    return FileStatusResponse(file_id=file_id, status=status)
