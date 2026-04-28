from pydantic import BaseModel, Field

from app.types.enums import FileStatus


class FileState(BaseModel):
    file_id: str = Field(description="Unique identifier for the uploaded file.")
    status: FileStatus = Field(description="Current ingestion status for the uploaded file.")


class FileUploadResponse(FileState):
    pass


class FileStatusResponse(FileState):
    pass
