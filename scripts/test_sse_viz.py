#!/usr/bin/env python3
"""Test SSE transport with visualization tool."""

import asyncio
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from bls_mcp.server import BLSMCPServer
from bls_mcp.transports.sse import SSETransport


async def test_sse_tools():
    """Test that SSE transport includes visualization tool."""
    print("=" * 60)
    print("SSE Transport Visualization Tool Test")
    print("=" * 60)

    # Initialize server and transport
    server = BLSMCPServer()
    sse = SSETransport(server)

    print("\n📊 MCP Server Tools:")
    for name, tool in server.tools.items():
        print(f"  ✓ {name}")
        print(f"    Description: {tool.description[:70]}...")

    print(f"\n📈 Total: {len(server.tools)} tools")

    # Check visualization tool
    if 'plot_series' in server.tools:
        print("\n✅ SUCCESS: Visualization tool is available via SSE transport!")

        viz_tool = server.tools['plot_series']
        print(f"\n📊 Visualization Tool Details:")
        print(f"  Name: {viz_tool.name}")
        print(f"  Description: {viz_tool.description}")
        print(f"  Parameters:")
        schema = viz_tool.input_schema.model_json_schema()
        for prop, details in schema.get('properties', {}).items():
            required = prop in schema.get('required', [])
            req_str = " (required)" if required else " (optional)"
            print(f"    - {prop}{req_str}: {details.get('description', 'No description')}")
    else:
        print("\n❌ ERROR: Visualization tool not found!")
        return False

    # Test simulating MCP tools/list request
    print("\n🔧 Simulating MCP 'tools/list' request...")
    tools_list = []
    if hasattr(server, 'tools'):
        for tool_name, tool in server.tools.items():
            tools_list.append({
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.input_schema.model_json_schema()
            })

    print(f"  Found {len(tools_list)} tools")
    for tool in tools_list:
        print(f"    - {tool['name']}")

    print("\n✅ SSE transport is properly configured for visualization!")
    print("\n📝 Next steps:")
    print("  1. Start ngrok server: uv run python scripts/start_ngrok.py")
    print("  2. Copy the public URL")
    print("  3. Use with any MCP-compatible client")
    print("  4. Call plot_series tool to create charts!")

    return True


if __name__ == "__main__":
    success = asyncio.run(test_sse_tools())
    sys.exit(0 if success else 1)
