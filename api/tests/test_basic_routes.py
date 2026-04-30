import unittest
from unittest.mock import patch

from app.api.routes.chat import chat
from app.api.routes.health import health
from app.schemas.chat import ChatRequest, ChatResponse


class TestBasicRoutes(unittest.TestCase):
    def test_health_returns_ok_status(self) -> None:
        payload = health()
        self.assertEqual(payload, {"status": "ok"})

    def test_chat_delegates_to_answer_question(self) -> None:
        request = ChatRequest(workspace_id="ws-1", question="hola")
        expected = ChatResponse(answer="ok", citations=[])

        with patch("app.api.routes.chat.answer_question", return_value=expected) as mocked:
            response = chat(request=request)

        mocked.assert_called_once_with(request=request)
        self.assertEqual(response, expected)
