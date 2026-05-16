#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT/back"

echo "==> back-quality: sync dev dependencies"
uv sync --group dev --quiet

echo "==> back-quality: mypy"
uv run mypy

echo "==> back-quality: ruff check"
uv run ruff check api db rag main.py utils.py

echo "==> back-quality: ruff format"
uv run ruff format --check api db rag main.py utils.py

echo "==> back-quality: pytest"
uv run pytest -q \
  --cov=api --cov=db --cov=rag --cov=main.py --cov=utils.py \
  --cov-report=term-missing:skip-covered

echo "==> back-quality: OK"
