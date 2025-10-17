#!/usr/bin/env bash
# Test BLS MCP server using uv

set -e

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Run test client with uv
uv run python scripts/test_mcp_client.py
