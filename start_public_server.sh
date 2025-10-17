#!/usr/bin/env bash
# Quick start script for BLS MCP Server with ngrok

echo "🚀 Starting BLS MCP Server with ngrok..."
echo "========================================"

cd /Users/rafaelkovashikawa/Downloads/projects/bls_food/bls_mcp

# Kill any existing ngrok processes
echo "🧹 Cleaning up existing processes..."
pkill -f ngrok 2>/dev/null || true

# Start the server
echo "🌐 Starting server with ngrok tunnel..."
uv run python scripts/start_ngrok.py
