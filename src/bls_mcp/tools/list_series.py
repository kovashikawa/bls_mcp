"""List series tool for browsing available BLS series."""

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from ..data.mock_data import MockDataProvider
from ..utils.logger import get_logger
from ..utils.validators import validate_limit
from .base import BaseTool

logger = get_logger(__name__)


class ListSeriesInput(BaseModel):
    """Input schema for list_series tool."""

    category: Optional[str] = Field(
        default=None,
        description="Filter by category (e.g., 'CPI', 'Employment'). Optional.",
    )
    limit: int = Field(
        default=50, description="Maximum number of results to return (default: 50)"
    )


class ListSeriesTool(BaseTool):
    """Tool for listing available BLS series."""

    def __init__(self, data_provider: MockDataProvider) -> None:
        """Initialize tool with data provider."""
        self.data_provider = data_provider

    @property
    def name(self) -> str:
        return "list_series"

    @property
    def description(self) -> str:
        return (
            "List available BLS data series with optional category filtering. "
            "Returns series metadata including titles, IDs, and categories."
        )

    @property
    def input_schema(self) -> type[BaseModel]:
        return ListSeriesInput

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute list_series tool."""
        logger.info(f"Executing list_series with arguments: {arguments}")

        # Validate input
        try:
            input_data = ListSeriesInput(**arguments)
        except Exception as e:
            logger.error(f"Input validation failed: {e}")
            return {"error": f"Invalid input: {str(e)}"}

        # Validate limit
        is_valid, error_msg = validate_limit(input_data.limit)
        if not is_valid:
            return {"error": error_msg}

        # List series
        try:
            series_list = await self.data_provider.list_series(
                category=input_data.category, limit=input_data.limit
            )
            logger.info(f"Successfully listed {len(series_list)} series")
            return {
                "series": series_list,
                "count": len(series_list),
                "category_filter": input_data.category,
            }
        except Exception as e:
            logger.error(f"Error listing series: {e}")
            return {"error": f"Failed to list series: {str(e)}"}
