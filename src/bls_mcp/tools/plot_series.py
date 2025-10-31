"""Tool for returning BLS data series in a format suitable for client-side plotting."""

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from ..utils.logger import get_logger
from ..utils.validators import validate_series_id, validate_year_range
from .base import BaseTool

logger = get_logger(__name__)


class PlotSeriesInput(BaseModel):
    """Input schema for plot_series tool."""

    series_id: str = Field(
        description="BLS series ID to plot (e.g., 'CUUR0000SA0' for CPI All Items)"
    )
    start_year: Optional[int] = Field(
        default=None, description="Start year for data range (optional)"
    )
    end_year: Optional[int] = Field(
        default=None, description="End year for data range (optional)"
    )


class PlotSeriesTool(BaseTool):
    """Tool for returning BLS data formatted for client-side plotting."""

    def __init__(self, data_provider: Any) -> None:
        """Initialize the plot series tool."""
        self.data_provider = data_provider

    @property
    def name(self) -> str:
        return "plot_series"

    @property
    def description(self) -> str:
        return (
            "Get BLS time series data formatted for plotting. "
            "Returns data with dates and values that can be used "
            "to create charts on the client side. Supports optional date filtering."
        )

    @property
    def input_schema(self) -> type[BaseModel]:
        return PlotSeriesInput

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the plot series tool."""
        logger.info(f"Executing plot_series with arguments: {arguments}")

        # Validate input
        try:
            input_data = PlotSeriesInput(**arguments)
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

        # Fetch data for this series
        try:
            series_data = await self.data_provider.get_series(
                series_id=input_data.series_id,
                start_year=input_data.start_year,
                end_year=input_data.end_year,
            )
        except ValueError as e:
            logger.warning(f"Series not found: {e}")
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"Failed to fetch series: {e}")
            return {"error": f"Failed to fetch series: {str(e)}"}

        # Extract data points
        data_points = series_data.get("data", [])
        if not data_points:
            return {"error": "No data available"}

        # Sort data chronologically and format for plotting (minimal format)
        plot_data = []
        for point in data_points:
            year = point["year"]
            month = point["period"].replace("M", "").zfill(2)
            # Format as YYYY-MM-DD (first day of month)
            date_str = f"{year}-{month}-01"
            value = float(point["value"])
            plot_data.append({
                "date": date_str,
                "value": value
            })

        # Sort oldest to newest
        plot_data.sort(key=lambda x: x["date"])

        # Get metadata
        metadata = series_data.get("metadata", {})
        series_title = metadata.get("series_title") or f"Series {input_data.series_id}"

        logger.info(
            f"Successfully formatted {len(plot_data)} data points for {input_data.series_id}"
        )

        return {
            "series_id": input_data.series_id,
            "title": series_title,
            "data": plot_data,
            "instructions": {
                "usage": [
                    "Use the data array as returned - do not reconstruct it manually",
                    "BLS data comes sorted oldest to newest - data is already in correct order",
                    "Do not truncate the series - plot all dates available in the response",
                    "Show exact Python/JavaScript that converts this JSON to a plot",
                    "If using pandas: df = pd.DataFrame(data['data']) then df['date'] = pd.to_datetime(df['date'])",
                    "Always sort by date ascending before plotting: df.sort_values('date')",
                    "For time series: use date as x-axis, value as y-axis",
                    "Do not fabricate monthly values - use only what comes from this response"
                ],
                "example_python": "import pandas as pd\nimport matplotlib.pyplot as plt\n\ndf = pd.DataFrame(data['data'])\ndf['date'] = pd.to_datetime(df['date'])\ndf = df.sort_values('date')\n\nplt.figure(figsize=(12, 6))\nplt.plot(df['date'], df['value'])\nplt.title(data['title'])\nplt.xlabel('Date')\nplt.ylabel('Index Value')\nplt.xticks(rotation=45)\nplt.tight_layout()\nplt.show()",
                "example_javascript": "const data = response.data;\nconst dates = data.map(d => d.date);\nconst values = data.map(d => d.value);\n\nnew Chart(ctx, {\n  type: 'line',\n  data: {\n    labels: dates,\n    datasets: [{\n      label: response.title,\n      data: values\n    }]\n  }\n});"
            }
        }
