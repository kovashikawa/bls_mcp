"""Get series tool for fetching BLS data."""

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from ..data.mock_data import MockDataProvider
from ..utils.logger import get_logger
from ..utils.validators import validate_series_id, validate_year_range
from .base import BaseTool

logger = get_logger(__name__)


class GetSeriesInput(BaseModel):
    """Input schema for get_series tool."""

    series_id: str = Field(
        description="BLS series ID (e.g., 'CUUR0000SA0' for CPI All Items)"
    )
    start_year: Optional[int] = Field(
        default=None, description="Start year for data range (optional)"
    )
    end_year: Optional[int] = Field(
        default=None, description="End year for data range (optional)"
    )


class GetSeriesTool(BaseTool):
    """Tool for fetching BLS data series."""

    def __init__(self, data_provider: MockDataProvider) -> None:
        """Initialize tool with data provider."""
        self.data_provider = data_provider

    @property
    def name(self) -> str:
        return "get_series"

    @property
    def description(self) -> str:
        return (
            "Fetch BLS data series by ID with optional date range filtering. "
            "Returns time series data points with values, periods, and metadata."
        )

    @property
    def input_schema(self) -> type[BaseModel]:
        return GetSeriesInput

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute get_series tool."""
        logger.info(f"Executing get_series with arguments: {arguments}")

        # Validate input
        try:
            input_data = GetSeriesInput(**arguments)
        except Exception as e:
            logger.error(f"Input validation failed: {e}")
            return {"error": f"Invalid input: {str(e)}"}

        # Validate series ID format
        if not validate_series_id(input_data.series_id):
            return {"error": f"Invalid series ID format: {input_data.series_id}"}

        # Validate year range
        is_valid, error_msg = validate_year_range(
            input_data.start_year, input_data.end_year
        )
        if not is_valid:
            return {"error": error_msg}

        # Fetch data
        try:
            result = await self.data_provider.get_series(
                series_id=input_data.series_id,
                start_year=input_data.start_year,
                end_year=input_data.end_year,
            )
            logger.info(
                f"Successfully fetched {result['count']} data points for {input_data.series_id}"
            )
            return result
        except ValueError as e:
            logger.warning(f"Series not found: {e}")
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"Error fetching series: {e}")
            return {"error": f"Failed to fetch series: {str(e)}"}
