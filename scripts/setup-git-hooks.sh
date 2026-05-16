#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
chmod +x "$ROOT/scripts/back-quality.sh" "$ROOT/.githooks/pre-push"
git -C "$ROOT" config core.hooksPath .githooks

echo "Git hooks enabled (core.hooksPath=.githooks)"
echo "pre-push will run: mypy, ruff check, ruff format --check, pytest"
