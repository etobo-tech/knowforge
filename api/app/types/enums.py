from enum import StrEnum


class FileStatus(StrEnum):
    PENDING = "pending"
    NOT_FOUND = "not_found"
    UNKNOWN = "unknown"
