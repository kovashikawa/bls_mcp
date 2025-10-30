#!/usr/bin/env bash
# Start BLS MCP server using uv

set -e

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Run server with uv (use full path for Claude Desktop compatibility)
/Users/rafaelkovashikawa/.local/bin/uv run python scripts/start_server.py
