#!/usr/bin/env bash
# Start BLS MCP server using uv

set -e

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Run server with uv
uv run python scripts/start_server.py
