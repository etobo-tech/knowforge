import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from app.services.ai_llm import build_openai_llm_client, generate_grounded_answer


class TestAiLlm(unittest.TestCase):
    def test_build_openai_llm_client_raises_without_api_key(self) -> None:
        settings = SimpleNamespace(openai_api_key=" ", openai_model="gpt-4o-mini")
        with patch("app.services.ai_llm.get_app_settings", return_value=settings):
            with self.assertRaises(RuntimeError):
                build_openai_llm_client()

    def test_build_openai_llm_client_uses_settings_values(self) -> None:
        settings = SimpleNamespace(openai_api_key="key-123", openai_model="gpt-4o-mini")
        with patch("app.services.ai_llm.get_app_settings", return_value=settings):
            with patch("app.services.ai_llm.OpenAI") as llm_cls:
                client = build_openai_llm_client()

        llm_cls.assert_called_once_with(
            model="gpt-4o-mini",
            api_key="key-123",
            temperature=0.1,
        )
        self.assertEqual(client, llm_cls.return_value)

    def test_generate_grounded_answer_builds_prompt_and_strips_output(self) -> None:
        llm = Mock()
        llm.complete.return_value = SimpleNamespace(text=" respuesta final \n")
        with patch("app.services.ai_llm.build_openai_llm_client", return_value=llm):
            answer = generate_grounded_answer(
                question="Que dice el documento?",
                context_chunks=["Uno", "Dos"],
            )

        prompt = llm.complete.call_args.args[0]
        self.assertIn("Question:\nQue dice el documento?", prompt)
        self.assertIn("[Context 1]\nUno", prompt)
        self.assertIn("[Context 2]\nDos", prompt)
        self.assertEqual(answer, "respuesta final")
