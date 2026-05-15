from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, UploadFile, status
from sqlalchemy.orm import Session

from db.session import get_db
from rag.upload import upload_document
from api.schemas.documents import DocumentResponse

DEV_USER_ID = UUID("00000000-0000-0000-0000-000000000001")

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentResponse)
async def upload_file(
    file: UploadFile,
    response: Response,
    db: Session = Depends(get_db),
):
    try:
        document, created = await upload_document(file, DEV_USER_ID, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    response.status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK

    return document
