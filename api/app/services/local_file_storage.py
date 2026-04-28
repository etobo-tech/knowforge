from dataclasses import dataclass
import json
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.constants import (
    JSON_FILE_ID_KEY,
    JSON_STATUS_KEY,
    LOCAL_STATUS_ROOT,
    LOCAL_STORAGE_ROOT,
)
from app.types.enums import FileStatus


@dataclass(frozen=True)
class StoredFile:
    file_id: str
    storage_path: Path
    status: FileStatus


def _safe_filename(*, raw_name: str) -> str:
    safe_name = Path(raw_name).name.strip()
    if not safe_name:
        raise ValueError("filename_required")
    return safe_name


def _status_path(*, file_id: str) -> Path:
    return LOCAL_STATUS_ROOT / f"{file_id}.json"


def _workspace_dir(*, workspace_id: str) -> Path:
    return LOCAL_STORAGE_ROOT / workspace_id


def _storage_path(*, workspace_id: str, file_id: str, safe_filename: str) -> Path:
    return _workspace_dir(workspace_id=workspace_id) / f"{file_id}_{safe_filename}"


def _write_status(*, file_id: str, status: FileStatus) -> None:
    LOCAL_STATUS_ROOT.mkdir(parents=True, exist_ok=True)
    status_path = _status_path(file_id=file_id)
    status_path.write_text(
        json.dumps(
            {
                JSON_FILE_ID_KEY: file_id,
                JSON_STATUS_KEY: status.value,
            }
        )
    )


def get_file_status(*, file_id: str) -> FileStatus:
    status_path = _status_path(file_id=file_id)
    if not status_path.exists():
        return FileStatus.NOT_FOUND

    payload = json.loads(status_path.read_text())
    status = payload.get(JSON_STATUS_KEY)
    if not isinstance(status, str):
        return FileStatus.UNKNOWN
    try:
        return FileStatus(status)
    except ValueError:
        return FileStatus.UNKNOWN


async def save_uploaded_file(
    *, workspace_id: str, uploaded_file: UploadFile
) -> StoredFile:
    file_id = str(uuid4())
    safe_filename = _safe_filename(raw_name=uploaded_file.filename or "")
    workspace_dir = _workspace_dir(workspace_id=workspace_id)
    workspace_dir.mkdir(parents=True, exist_ok=True)

    storage_path = _storage_path(
        workspace_id=workspace_id,
        file_id=file_id,
        safe_filename=safe_filename,
    )
    content = await uploaded_file.read()
    storage_path.write_bytes(content)

    _write_status(file_id=file_id, status=FileStatus.PENDING)

    return StoredFile(
        file_id=file_id,
        storage_path=storage_path,
        status=FileStatus.PENDING,
    )
