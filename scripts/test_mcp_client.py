#!/usr/bin/env python3
"""Test client for BLS MCP server."""

import asyncio
import json
import subprocess
import sys
from pathlib import Path


async def test_mcp_server():
    """Test the MCP server with various requests."""
    print("🧪 Testing BLS MCP Server")
    print("=" * 60)

    # Path to server script
    server_script = Path(__file__).parent / "start_server.py"

    # Test requests
    requests = [
        # Initialize
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"},
            },
        },
        # List tools
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
        # List all series
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": "list_series", "arguments": {"limit": 5}},
        },
        # Get series info
        {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "get_series_info",
                "arguments": {"series_id": "CUUR0000SA0"},
            },
        },
        # Get series data
        {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "get_series",
                "arguments": {
                    "series_id": "CUUR0000SA0",
                    "start_year": 2023,
                    "end_year": 2024,
                },
            },
        },
        # Plot series
        {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "tools/call",
            "params": {
                "name": "plot_series",
                "arguments": {
                    "series_id": "CUUR0000SA0",
                    "start_year": 2023,
                    "end_year": 2024,
                    "chart_type": "line",
                },
            },
        },
    ]

    # Prepare input
    input_data = "\n".join(json.dumps(req) for req in requests)

    print("\n📤 Sending requests to MCP server...\n")

    # Start server process
    try:
        process = subprocess.Popen(
            [sys.executable, str(server_script)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # Send requests and get responses
        stdout, stderr = process.communicate(input=input_data, timeout=10)

        print("📥 Responses received:\n")
        print("=" * 60)

        # Parse and display responses
        for i, line in enumerate(stdout.strip().split("\n"), 1):
            if line.strip():
                try:
                    response = json.loads(line)
                    print(f"\n📋 Response {i}:")

                    # Check if response contains image content
                    if "result" in response and "content" in response["result"]:
                        content = response["result"]["content"]
                        if isinstance(content, list):
                            for item in content:
                                if isinstance(item, dict) and item.get("type") == "image":
                                    # Truncate base64 image data for display
                                    item_copy = item.copy()
                                    if "data" in item_copy:
                                        data_len = len(item_copy["data"])
                                        item_copy["data"] = f"<base64 image data: {data_len} chars>"
                                    print(json.dumps({"type": "image", **item_copy}, indent=2))
                                    print(f"  ✅ Image content detected! ({data_len} chars)")
                                    continue

                    print(json.dumps(response, indent=2))
                except json.JSONDecodeError:
                    print(f"⚠️  Could not parse response: {line}")

        if stderr:
            print("\n" + "=" * 60)
            print("📋 Server logs (stderr):")
            print("=" * 60)
            print(stderr)

        print("\n" + "=" * 60)
        print("✅ Test completed successfully!")

    except subprocess.TimeoutExpired:
        print("❌ Test timed out")
        process.kill()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_mcp_server())
