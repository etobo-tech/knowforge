from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, UploadFile, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from db.models import Document
from db.session import get_db
from db.repositories.documents import (
    db_delete_document,
    db_get_document_for_user,
    db_list_documents_for_user,
)
from rag.upload import upload_document
from rag.s3 import delete_object_from_s3, presigned_download_url
from api.schemas.documents import DocumentResponse

DEV_USER_ID = UUID("00000000-0000-0000-0000-000000000001")

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", response_model=list[DocumentResponse])
def list_documents(db: Session = Depends(get_db)) -> list[Document]:
    return db_list_documents_for_user(db, DEV_USER_ID)


@router.get("/{document_id}/download")
def download_document(
    document_id: UUID, db: Session = Depends(get_db)
) -> RedirectResponse:
    document = db_get_document_for_user(db, DEV_USER_ID, document_id)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    try:
        url = presigned_download_url(document.s3_key, document.filename)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not prepare download",
        )
    return RedirectResponse(url=url, status_code=status.HTTP_302_FOUND)


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(document_id: UUID, db: Session = Depends(get_db)) -> Document:
    document = db_get_document_for_user(db, DEV_USER_ID, document_id)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: UUID, db: Session = Depends(get_db)
) -> Response:
    document = db_get_document_for_user(db, DEV_USER_ID, document_id)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    s3_key = document.s3_key
    db_delete_document(db, document)
    try:
        delete_object_from_s3(s3_key)
    except Exception:
        pass
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/upload", response_model=DocumentResponse)
async def upload_file(
    file: UploadFile,
    response: Response,
    db: Session = Depends(get_db),
) -> Document:
    try:
        document, created = await upload_document(file, DEV_USER_ID, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    response.status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK

    return document
