#!/usr/bin/env python3
"""Start the BLS MCP server with stdio transport."""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from bls_mcp.server import main

if __name__ == "__main__":
    main()
