import runpy

import pytest

import main as back_main


def test_main_prints_message(capsys: pytest.CaptureFixture[str]) -> None:
    back_main.main()
    captured = capsys.readouterr()
    assert "Hello from back!" in captured.out


def test_main_module_entrypoint(capsys: pytest.CaptureFixture[str]) -> None:
    runpy.run_module("main", run_name="__main__")
    captured = capsys.readouterr()
    assert "Hello from back!" in captured.out
