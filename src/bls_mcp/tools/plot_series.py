"""Tool for returning BLS data series in a format suitable for client-side plotting."""

from typing import Any, Dict

from pydantic import BaseModel

from ..data.mock_data import MockDataProvider
from ..utils.logger import get_logger
from .base import BaseTool

logger = get_logger(__name__)


class PlotSeriesInput(BaseModel):
    """Input schema for plot_series tool - no parameters needed."""
    pass


class PlotSeriesTool(BaseTool):
    """Tool for returning CPI All Items (CUUR0000SA0) data for client-side plotting."""

    def __init__(self, data_provider: MockDataProvider) -> None:
        """Initialize the plot series tool."""
        self.data_provider = data_provider

    @property
    def name(self) -> str:
        return "plot_series"

    @property
    def description(self) -> str:
        return (
            "Get CPI All Items (CUUR0000SA0) data formatted for plotting. "
            "Returns time series data with dates and values that can be used "
            "to create charts on the client side. No parameters needed."
        )

    @property
    def input_schema(self) -> type[BaseModel]:
        return PlotSeriesInput

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the plot series tool - returns data for CUUR0000SA0."""
        logger.info("Executing plot_series for CUUR0000SA0")

        # Hardcoded series
        series_id = "CUUR0000SA0"

        # Fetch ALL available data for this series
        try:
            series_data = await self.data_provider.get_series(series_id)
        except Exception as e:
            logger.error(f"Failed to fetch series: {e}")
            return {"status": "error", "error": str(e)}

        # Extract data points
        data_points = series_data.get("data", [])
        if not data_points:
            return {"status": "error", "error": "No data available"}

        # Sort data chronologically and format for plotting
        plot_data = []
        for point in data_points:
            year = point["year"]
            month = point["period"].replace("M", "").zfill(2)
            date_str = f"{year}-{month}"
            value = float(point["value"])
            plot_data.append({
                "date": date_str,
                "value": value,
                "year": year,
                "month": month,
                "period": point["period"]
            })

        # Sort oldest to newest
        plot_data.sort(key=lambda x: x["date"])

        # Calculate statistics
        values = [d["value"] for d in plot_data]
        min_value = min(values)
        max_value = max(values)
        avg_value = sum(values) / len(values)

        # Get metadata
        metadata = series_data.get("metadata", {})

        return {
            "status": "success",
            "series_id": series_id,
            "series_title": metadata.get("series_title", "CPI All Urban Consumers: All Items"),
            "data": plot_data,
            "statistics": {
                "count": len(plot_data),
                "min": round(min_value, 3),
                "max": round(max_value, 3),
                "average": round(avg_value, 3),
            },
            "date_range": {
                "start": plot_data[0]["date"],
                "end": plot_data[-1]["date"]
            },
            "plot_instructions": {
                "chart_type": "line",
                "x_axis": "date",
                "y_axis": "value",
                "title": metadata.get("series_title", "CPI All Urban Consumers: All Items"),
                "y_label": "Index Value",
                "x_label": "Date"
            }
        }
