#!/usr/bin/env bash
# Test BLS MCP server using uv

set -e

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Run test client with uv (use full path for Claude Desktop compatibility)
/Users/rafaelkovashikawa/.local/bin/uv run python scripts/test_mcp_client.py
