from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.core.constants import SUPPORTED_SUFFIXES
from app.core.settings import get_app_settings
from app.schemas.files import FileStatusResponse, FileUploadResponse
from app.services.local_file_storage import (
    get_file_status as get_stored_file_status,
)
from app.services.local_file_storage import save_uploaded_file

router = APIRouter(prefix="/files", tags=["files"])
FILE_POINTER_START = 0
FILE_POINTER_END = 2


def _raise_bad_request(*, detail: str) -> None:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=detail,
    )


def _validate_filename(*, uploaded_file: UploadFile) -> None:
    if not (uploaded_file.filename or "").strip():
        _raise_bad_request(detail="filename_required")


def _validate_suffix(*, uploaded_file: UploadFile) -> None:
    if Path(uploaded_file.filename or "").suffix.lower() not in SUPPORTED_SUFFIXES:
        _raise_bad_request(detail="unsupported_file_type")


def _get_upload_size(*, uploaded_file: UploadFile) -> int:
    uploaded_file.file.seek(FILE_POINTER_START, FILE_POINTER_END)
    file_size = uploaded_file.file.tell()
    uploaded_file.file.seek(FILE_POINTER_START)
    return file_size


def _validate_upload_size(*, uploaded_file: UploadFile, max_bytes: int) -> None:
    if _get_upload_size(uploaded_file=uploaded_file) > max_bytes:
        _raise_bad_request(detail="file_too_large")


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    *,
    workspace_id: str = Form(...),
    uploaded_file: UploadFile = File(...),
) -> FileUploadResponse:
    _validate_filename(uploaded_file=uploaded_file)
    _validate_suffix(uploaded_file=uploaded_file)
    _validate_upload_size(
        uploaded_file=uploaded_file,
        max_bytes=get_app_settings().max_upload_bytes,
    )

    stored_file = await save_uploaded_file(
        workspace_id=workspace_id,
        uploaded_file=uploaded_file,
    )
    return FileUploadResponse(file_id=stored_file.file_id, status=stored_file.status)


@router.get("/{file_id}/status", response_model=FileStatusResponse)
def get_file_status(*, file_id: str) -> FileStatusResponse:
    status = get_stored_file_status(file_id=file_id)
    return FileStatusResponse(file_id=file_id, status=status)
