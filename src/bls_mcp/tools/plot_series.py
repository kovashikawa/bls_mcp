"""Tool for creating simple static plots of BLS data series."""

import base64
from io import BytesIO
from typing import Any, Dict, Optional

try:
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    import numpy as np
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

from pydantic import BaseModel, Field

from ..data.mock_data import MockDataProvider
from ..utils.logger import get_logger
from .base import BaseTool

logger = get_logger(__name__)


class PlotSeriesInput(BaseModel):
    """Input schema for plot_series tool."""

    series_id: str = Field(
        description="BLS series ID to plot (e.g., 'CUUR0000SA0')"
    )
    start_year: Optional[int] = Field(
        default=None, description="Start year for data range (optional)"
    )
    end_year: Optional[int] = Field(
        default=None, description="End year for data range (optional)"
    )
    chart_type: str = Field(
        default="line",
        description="Type of chart to create: 'line' or 'bar' (default: 'line')",
    )


class PlotSeriesTool(BaseTool):
    """Tool for creating simple static plots of BLS data series.

    This tool generates a simple visualization of BLS time series data
    and returns it as a base64-encoded PNG image that can be displayed
    in LLM interfaces.

    Features:
    - Line plots for time series trends
    - Bar plots for comparing values
    - Automatic date formatting
    - Clean, readable design
    """

    def __init__(self, data_provider: MockDataProvider) -> None:
        """Initialize the plot series tool.

        Args:
            data_provider: Data provider instance for fetching series data
        """
        self.data_provider = data_provider
        if not MATPLOTLIB_AVAILABLE:
            raise ImportError(
                "matplotlib is required for visualization tools. "
                "Install with: uv sync --extra viz"
            )

    @property
    def name(self) -> str:
        return "plot_series"

    @property
    def description(self) -> str:
        return (
            "Create a simple static plot (line or bar chart) of a BLS data series. "
            "Returns a base64-encoded PNG image that can be displayed. "
            "Useful for visualizing CPI trends, comparing time periods, or "
            "identifying patterns in the data."
        )

    @property
    def input_schema(self) -> type[BaseModel]:
        return PlotSeriesInput

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the plot series tool.

        Args:
            arguments: Tool arguments (series_id, start_year, end_year, chart_type)

        Returns:
            dict with status, series info, and base64-encoded image
        """
        logger.info(f"Executing plot_series with arguments: {arguments}")

        # Validate input
        try:
            inputs = PlotSeriesInput(**arguments)
        except Exception as e:
            logger.error(f"Input validation failed: {e}")
            return {"status": "error", "error": f"Invalid input: {str(e)}"}

        # Fetch series data
        try:
            series_data = await self.data_provider.get_series(
                inputs.series_id, inputs.start_year, inputs.end_year
            )
        except ValueError as e:
            logger.error(f"Failed to fetch series: {e}")
            return {
                "status": "error",
                "error": str(e),
            }
        except Exception as e:
            logger.error(f"Unexpected error fetching series: {e}")
            return {
                "status": "error",
                "error": f"Failed to fetch series: {str(e)}",
            }

        # Get series metadata
        try:
            metadata = await self.data_provider.get_series_info(inputs.series_id)
        except Exception as e:
            logger.warning(f"Failed to fetch metadata: {e}")
            metadata = {"title": inputs.series_id}

        # Extract data points
        data_points = series_data.get("data", [])
        if not data_points:
            return {
                "status": "error",
                "error": "No data points available for the specified range",
            }

        # Parse dates and values, then sort chronologically
        # BLS API returns data in reverse chronological order (newest first)
        data_tuples = []
        for point in data_points:
            # Format: YYYY-MM (e.g., "2023-01")
            year = point["year"]
            period = point["period"]
            # Period format is M01, M02, etc.
            month = period.replace("M", "").zfill(2)  # Ensure 2-digit month
            date_str = f"{year}-{month}"
            value = float(point["value"])
            data_tuples.append((date_str, value))

        # Sort by date (oldest first)
        data_tuples.sort(key=lambda x: x[0])

        # Extract sorted dates and values
        dates = [d[0] for d in data_tuples]
        values = [d[1] for d in data_tuples]

        # Create the plot
        fig, ax = plt.subplots(figsize=(10, 6))

        if inputs.chart_type == "bar":
            ax.bar(range(len(values)), values, color='steelblue', alpha=0.7)
            ax.set_xticks(range(len(dates)))
            ax.set_xticklabels(dates, rotation=45, ha='right')
        else:  # line chart (default)
            ax.plot(range(len(values)), values, marker='o', linewidth=2,
                   markersize=4, color='steelblue')
            ax.set_xticks(range(len(dates)))
            ax.set_xticklabels(dates, rotation=45, ha='right')
            ax.grid(True, alpha=0.3)

        # Set labels and title
        title = metadata.get("title", inputs.series_id)
        ax.set_title(f"{title}\n{dates[0]} to {dates[-1]}", fontsize=12, pad=20)
        ax.set_xlabel("Date", fontsize=10)
        ax.set_ylabel("Value", fontsize=10)

        # Adjust layout to prevent label cutoff
        plt.tight_layout()

        # Convert plot to base64-encoded PNG
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close(fig)

        result = {
            "status": "success",
            "series_id": inputs.series_id,
            "title": title,
            "chart_type": inputs.chart_type,
            "data_points": len(data_points),
            "date_range": {
                "start": dates[0],
                "end": dates[-1],
            },
            "value_range": {
                "min": min(values),
                "max": max(values),
                "mean": sum(values) / len(values),
            },
            "image": {
                "format": "png",
                "encoding": "base64",
                "data": image_base64,
            },
            "message": (
                f"Created {inputs.chart_type} chart for {title} "
                f"with {len(data_points)} data points"
            ),
        }

        logger.info(f"Successfully created {inputs.chart_type} plot for {inputs.series_id}")
        return result
