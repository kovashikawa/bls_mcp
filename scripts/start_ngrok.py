#!/usr/bin/env python3
"""Start the BLS MCP server with ngrok tunnel for remote access."""

import asyncio
import os
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from pyngrok import ngrok
from bls_mcp.server import BLSMCPServer
from bls_mcp.utils.logger import get_logger, setup_logging

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Setup logging
log_level = os.getenv("LOG_LEVEL", "INFO")
setup_logging(log_level)
logger = get_logger(__name__)

# Configuration
MCP_SERVER_PORT = int(os.getenv("MCP_SERVER_PORT", "3000"))
MCP_SERVER_HOST = os.getenv("MCP_SERVER_HOST", "localhost")


async def main():
    """Start MCP server with ngrok tunnel."""
    logger.info("🚀 Starting BLS MCP Server with ngrok tunnel")
    
    try:
        # Clean up any existing tunnels first
        logger.info("🧹 Cleaning up existing ngrok tunnels...")
        try:
            ngrok.kill()
        except:
            pass
        
        # Start ngrok tunnel
        logger.info(f"🌐 Creating ngrok tunnel for port {MCP_SERVER_PORT}")
        public_url = ngrok.connect(MCP_SERVER_PORT, bind_tls=True)
        
        logger.info(f"✅ ngrok tunnel created successfully!")
        logger.info(f"🔗 Public URL: {public_url}")
        logger.info(f"📡 Local server: http://{MCP_SERVER_HOST}:{MCP_SERVER_PORT}")
        
        # Start MCP server
        logger.info("🎯 Starting MCP server...")
        server = BLSMCPServer()
        
        # Start SSE server for remote access
        logger.info("🌐 Starting SSE transport for remote access...")
        from bls_mcp.transports.sse import SSETransport
        
        sse_transport = SSETransport(server)
        await sse_transport.run(host=MCP_SERVER_HOST, port=MCP_SERVER_PORT)
        
    except KeyboardInterrupt:
        logger.info("🛑 Shutting down server...")
    except Exception as e:
        logger.error(f"❌ Error starting server: {e}")
        raise
    finally:
        # Clean up ngrok tunnel
        try:
            ngrok.disconnect(public_url)
            ngrok.kill()
            logger.info("🧹 ngrok tunnel closed")
        except:
            pass


if __name__ == "__main__":
    asyncio.run(main())
