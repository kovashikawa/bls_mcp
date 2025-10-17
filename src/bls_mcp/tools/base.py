"""Base tool class for BLS MCP tools."""

from abc import ABC, abstractmethod
from typing import Any, Dict

from pydantic import BaseModel


class BaseTool(ABC):
    """Base class for MCP tools."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description."""
        pass

    @property
    @abstractmethod
    def input_schema(self) -> type[BaseModel]:
        """Pydantic model for input validation."""
        pass

    @abstractmethod
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the tool with given arguments.

        Args:
            arguments: Tool arguments as dictionary

        Returns:
            Tool execution result

        Raises:
            ValueError: If validation fails
        """
        pass

    def to_mcp_tool(self) -> Dict[str, Any]:
        """
        Convert tool to MCP tool definition.

        Returns:
            MCP tool definition dictionary
        """
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema.model_json_schema(),
        }
