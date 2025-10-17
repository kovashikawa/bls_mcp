#!/usr/bin/env bash
# Run tests using uv

set -e

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Install dev dependencies if needed
uv sync --all-extras

# Run tests with uv
uv run pytest tests/ -v "$@"
