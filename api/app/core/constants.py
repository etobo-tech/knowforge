from pathlib import Path

LOCAL_STORAGE_ROOT = Path("data/uploads")
LOCAL_STATUS_ROOT = Path("data/status")
LOCAL_CHUNKS_ROOT = Path("data/chunks")

JSON_FILE_ID_KEY = "file_id"
JSON_STATUS_KEY = "status"

CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
SUPPORTED_SUFFIXES = frozenset({".txt", ".md"})
CHAT_TOP_K = 3
