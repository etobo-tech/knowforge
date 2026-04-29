from enum import StrEnum


class FileStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"
    NOT_FOUND = "not_found"
    UNKNOWN = "unknown"
