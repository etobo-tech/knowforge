import unittest

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes.chat import router as chat_router
from app.api.routes.files import router as files_router
from app.api.routes.health import router as health_router


def create_test_app() -> FastAPI:
    app = FastAPI(title="Knowforge API Test")
    app.include_router(health_router)
    app.include_router(files_router)
    app.include_router(chat_router)
    return app


class TestFilesUploadRoute(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(create_test_app())

    def test_rejects_unsupported_file_type(self) -> None:
        response = self.client.post(
            "/files/upload",
            data={"workspace_id": "ws-test"},
            files={"uploaded_file": ("notes.pdf", b"dummy", "application/pdf")},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"detail": "unsupported_file_type"})
