"""Get series info tool for fetching series metadata."""

from typing import Any, Dict

from pydantic import BaseModel, Field

from ..data.mock_data import MockDataProvider
from ..utils.logger import get_logger
from ..utils.validators import validate_series_id
from .base import BaseTool

logger = get_logger(__name__)


class GetSeriesInfoInput(BaseModel):
    """Input schema for get_series_info tool."""

    series_id: str = Field(description="BLS series ID (e.g., 'CUUR0000SA0')")


class GetSeriesInfoTool(BaseTool):
    """Tool for getting BLS series metadata."""

    def __init__(self, data_provider: MockDataProvider) -> None:
        """Initialize tool with data provider."""
        self.data_provider = data_provider

    @property
    def name(self) -> str:
        return "get_series_info"

    @property
    def description(self) -> str:
        return (
            "Get detailed metadata information about a specific BLS series. "
            "Returns series title, description, category, and data availability."
        )

    @property
    def input_schema(self) -> type[BaseModel]:
        return GetSeriesInfoInput

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute get_series_info tool."""
        logger.info(f"Executing get_series_info with arguments: {arguments}")

        # Validate input
        try:
            input_data = GetSeriesInfoInput(**arguments)
        except Exception as e:
            logger.error(f"Input validation failed: {e}")
            return {"error": f"Invalid input: {str(e)}"}

        # Validate series ID format
        if not validate_series_id(input_data.series_id):
            return {"error": f"Invalid series ID format: {input_data.series_id}"}

        # Get series info
        try:
            info = await self.data_provider.get_series_info(
                series_id=input_data.series_id
            )
            logger.info(f"Successfully retrieved info for {input_data.series_id}")
            return info
        except ValueError as e:
            logger.warning(f"Series not found: {e}")
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"Error getting series info: {e}")
            return {"error": f"Failed to get series info: {str(e)}"}
