import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.services import local_file_storage
from app.types.enums import FileStatus


class TestLocalFileStorage(unittest.TestCase):
    def test_safe_filename_keeps_basename(self) -> None:
        safe = local_file_storage._safe_filename(raw_name="nested/path/notes.md")
        self.assertEqual(safe, "notes.md")

    def test_safe_filename_raises_when_empty(self) -> None:
        with self.assertRaises(ValueError):
            local_file_storage._safe_filename(raw_name="   ")

    def test_get_file_status_returns_not_found_when_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            with patch.object(local_file_storage, "LOCAL_STATUS_ROOT", Path(tmp_dir)):
                status = local_file_storage.get_file_status(file_id="missing-file")
                self.assertEqual(status, FileStatus.NOT_FOUND)

    def test_get_file_status_returns_written_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            with patch.object(local_file_storage, "LOCAL_STATUS_ROOT", Path(tmp_dir)):
                local_file_storage._write_status(
                    file_id="file-1",
                    status=FileStatus.READY,
                )
                status = local_file_storage.get_file_status(file_id="file-1")
                self.assertEqual(status, FileStatus.READY)

    def test_get_file_status_returns_unknown_for_invalid_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            status_root = Path(tmp_dir)
            with patch.object(local_file_storage, "LOCAL_STATUS_ROOT", status_root):
                status_root.mkdir(parents=True, exist_ok=True)
                (status_root / "file-2.json").write_text(json.dumps({"status": 123}))
                status = local_file_storage.get_file_status(file_id="file-2")
                self.assertEqual(status, FileStatus.UNKNOWN)

    def test_chunk_text_returns_empty_for_blank_input(self) -> None:
        chunks = local_file_storage._chunk_text(text="   ")
        self.assertEqual(chunks, [])
