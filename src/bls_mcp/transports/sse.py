"""SSE transport implementation for remote MCP server access."""

import asyncio
import json
from typing import Any, Dict, Optional

from sse_starlette import EventSourceResponse
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from ..utils.logger import get_logger

logger = get_logger(__name__)


class SSETransport:
    """Server-Sent Events transport for MCP server."""
    
    def __init__(self, mcp_server):
        self.mcp_server = mcp_server
        self.app = self._create_app()
    
    def _create_app(self):
        """Create Starlette app with SSE endpoints."""
        
        async def health_check(request: Request):
            """Health check endpoint."""
            return JSONResponse({"status": "healthy", "transport": "sse"})
        
        async def root_endpoint(request: Request):
            """Root endpoint with server information."""
            return JSONResponse({
                "name": "BLS MCP Server",
                "version": "1.18.0",
                "transport": "SSE",
                "endpoints": {
                    "health": "/health",
                    "mcp": "/mcp (POST only)",
                    "sse": "/sse"
                },
                "description": "Bureau of Labor Statistics data server via MCP protocol"
            })
        
        async def mcp_info(request: Request):
            """MCP endpoint info (GET request)."""
            return JSONResponse({
                "message": "MCP endpoint - use POST requests",
                "methods": ["initialize", "tools/list", "tools/call"],
                "example": {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/list",
                    "params": {}
                }
            })
        
        async def sse_endpoint(request: Request):
            """SSE endpoint for MCP communication."""
            async def event_generator():
                try:
                    # Send initial connection event
                    yield {
                        "event": "connected",
                        "data": json.dumps({
                            "type": "connection",
                            "status": "established"
                        })
                    }
                    
                    # Keep connection alive
                    while True:
                        await asyncio.sleep(1)
                        yield {
                            "event": "ping",
                            "data": json.dumps({"type": "ping"})
                        }
                        
                except asyncio.CancelledError:
                    logger.info("SSE connection cancelled")
                except Exception as e:
                    logger.error(f"SSE error: {e}")
            
            return EventSourceResponse(event_generator())
        
        async def handle_mcp_request(request: Request):
            """Handle MCP requests via HTTP POST."""
            try:
                body = await request.json()
                logger.debug(f"Received MCP request: {body}")
                
                # Process MCP request through the actual MCP server
                method = body.get("method")
                params = body.get("params", {})
                request_id = body.get("id")
                
                if method == "initialize":
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "protocolVersion": "2024-11-05",
                            "capabilities": {
                                "experimental": {},
                                "tools": {"listChanged": False}
                            },
                            "serverInfo": {
                                "name": "bls-mcp-server",
                                "version": "1.18.0"
                            }
                        }
                    }
                elif method == "tools/list":
                    tools = [
                        {
                            "name": "get_series",
                            "description": "Fetch BLS data series by ID with optional date range filtering",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "series_id": {"type": "string", "description": "BLS series ID"},
                                    "start_year": {"type": "integer", "description": "Start year"},
                                    "end_year": {"type": "integer", "description": "End year"}
                                },
                                "required": ["series_id"]
                            }
                        },
                        {
                            "name": "list_series",
                            "description": "List available BLS data series",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "category": {"type": "string", "description": "Filter by category"},
                                    "limit": {"type": "integer", "description": "Maximum results"}
                                }
                            }
                        },
                        {
                            "name": "get_series_info",
                            "description": "Get detailed metadata about a series",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "series_id": {"type": "string", "description": "BLS series ID"}
                                },
                                "required": ["series_id"]
                            }
                        }
                    ]
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {"tools": tools}
                    }
                elif method == "tools/call":
                    tool_name = params.get("name")
                    arguments = params.get("arguments", {})
                    
                    # Call the actual MCP server tool
                    if hasattr(self.mcp_server, 'tools') and tool_name in self.mcp_server.tools:
                        tool = self.mcp_server.tools[tool_name]
                        result = await tool.execute(arguments)
                        response = {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "result": {
                                "content": [{"type": "text", "text": str(result)}],
                                "isError": False
                            }
                        }
                    else:
                        response = {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}
                        }
                else:
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {"code": -32601, "message": f"Unknown method: {method}"}
                    }
                
                return JSONResponse(response)
                
            except Exception as e:
                logger.error(f"Error handling MCP request: {e}")
                return JSONResponse(
                    {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32603, "message": str(e)}},
                    status_code=500
                )
        
        # Create Starlette app
        app = Starlette(
            routes=[
                Route("/", root_endpoint),
                Route("/health", health_check),
                Route("/sse", sse_endpoint),
                Route("/mcp", handle_mcp_request, methods=["POST"]),
                Route("/mcp", mcp_info, methods=["GET"]),
            ],
            middleware=[
                Middleware(
                    CORSMiddleware,
                    allow_origins=["*"],
                    allow_credentials=True,
                    allow_methods=["*"],
                    allow_headers=["*"],
                )
            ]
        )
        
        return app
    
    async def run(self, host: str = "localhost", port: int = 3000):
        """Run the SSE server."""
        import uvicorn
        
        logger.info(f"Starting SSE server on {host}:{port}")
        logger.info(f"Health check: http://{host}:{port}/health")
        logger.info(f"SSE endpoint: http://{host}:{port}/sse")
        logger.info(f"MCP endpoint: http://{host}:{port}/mcp")
        
        config = uvicorn.Config(
            app=self.app,
            host=host,
            port=port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()
