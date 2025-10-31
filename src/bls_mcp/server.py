"""Main MCP server implementation for BLS data."""

import asyncio
import os
from typing import Any, Sequence

from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .data.db_data_provider import DatabaseDataProvider
from .tools.get_series import GetSeriesTool
from .tools.get_series_info import GetSeriesInfoTool
from .tools.list_series import ListSeriesTool
from .utils.logger import get_logger, setup_logging

# Import visualization tool (no longer requires matplotlib)
from .tools.plot_series import PlotSeriesTool

# Load environment variables
load_dotenv()

# Setup logging
log_level = os.getenv("LOG_LEVEL", "INFO")
setup_logging(log_level)

logger = get_logger(__name__)


class BLSMCPServer:
    """BLS MCP Server implementation."""

    def __init__(self) -> None:
        """Initialize BLS MCP server."""
        logger.info("Initializing BLS MCP Server")

        # Create MCP server
        self.server = Server("bls-mcp-server")

        # Initialize database data provider
        logger.info("Initializing database data provider")
        try:
            self.data_provider = DatabaseDataProvider()
            logger.info("Database provider initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database provider: {e}")
            logger.error("Cannot start server without database connection")
            raise RuntimeError(
                "Database connection required. "
                "Please ensure PostgreSQL is running and configured in .env"
            ) from e

        # Initialize tools
        self.tools = {
            "get_series": GetSeriesTool(self.data_provider),
            "list_series": ListSeriesTool(self.data_provider),
            "get_series_info": GetSeriesInfoTool(self.data_provider),
            "plot_series": PlotSeriesTool(self.data_provider),
        }

        logger.info("All tools registered (including plot_series)")

        # Register handlers
        self._register_handlers()

        logger.info("BLS MCP Server initialized successfully")

    def _register_handlers(self) -> None:
        """Register MCP protocol handlers."""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available tools."""
            logger.debug("Listing tools")
            return [
                Tool(
                    name=tool.name,
                    description=tool.description,
                    inputSchema=tool.input_schema.model_json_schema(),
                )
                for tool in self.tools.values()
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict[str, Any]) -> Sequence[TextContent]:
            """Call a tool by name with arguments."""
            logger.info(f"Tool called: {name}")
            logger.debug(f"Arguments: {arguments}")

            if name not in self.tools:
                error_msg = f"Unknown tool: {name}"
                logger.error(error_msg)
                return [TextContent(type="text", text=f"Error: {error_msg}")]

            tool = self.tools[name]

            try:
                result = await tool.execute(arguments)
                logger.info(f"Tool {name} returned status: {result.get('status')}")

                # Convert result to JSON string for text content
                import json

                # Return as JSON text (all tools now return data, no images)
                logger.info("Returning JSON text response")
                result_text = json.dumps(result, indent=2)
                return [TextContent(type="text", text=result_text)]

            except Exception as e:
                error_msg = f"Tool execution failed: {str(e)}"
                logger.error(error_msg, exc_info=True)
                return [TextContent(type="text", text=f"Error: {error_msg}")]

    async def run_stdio(self) -> None:
        """Run server with stdio transport."""
        logger.info("Starting MCP server with stdio transport")

        async with stdio_server() as (read_stream, write_stream):
            logger.info("stdio streams established")
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options(),
            )


def main() -> None:
    """Main entry point for stdio server."""
    server = BLSMCPServer()
    asyncio.run(server.run_stdio())


if __name__ == "__main__":
    main()
