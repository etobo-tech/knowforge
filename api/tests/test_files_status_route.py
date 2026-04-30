import unittest
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes.files import router as files_router
from app.api.routes.health import router as health_router
from app.types.enums import FileStatus


def create_test_app() -> FastAPI:
    app = FastAPI(title="Knowforge API Test")
    app.include_router(health_router)
    app.include_router(files_router)
    return app


class TestFilesStatusRoute(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(create_test_app())

    @patch("app.api.routes.files.get_stored_file_status")
    def test_returns_not_found_status(self, mock_get_status) -> None:
        mock_get_status.return_value = FileStatus.NOT_FOUND

        response = self.client.get("/files/file-123/status")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "file_id": "file-123",
                "status": "not_found",
            },
        )

    @patch("app.api.routes.files.get_stored_file_status")
    def test_returns_ready_status(self, mock_get_status) -> None:
        mock_get_status.return_value = FileStatus.READY

        response = self.client.get("/files/file-456/status")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "file_id": "file-456",
                "status": "ready",
            },
        )
