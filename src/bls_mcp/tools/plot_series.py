"""Tool for creating simple static plots of BLS data series."""

import base64
from io import BytesIO
from typing import Any, Dict

try:
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

from pydantic import BaseModel

from ..data.mock_data import MockDataProvider
from ..utils.logger import get_logger
from .base import BaseTool

logger = get_logger(__name__)


class PlotSeriesInput(BaseModel):
    """Input schema for plot_series tool - no parameters needed."""
    pass


class PlotSeriesTool(BaseTool):
    """Simple tool for plotting CUUR0000SA0 (CPI All Items)."""

    def __init__(self, data_provider: MockDataProvider) -> None:
        """Initialize the plot series tool."""
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
        return "Create a simple line plot of CPI All Items (CUUR0000SA0). No parameters needed."

    @property
    def input_schema(self) -> type[BaseModel]:
        return PlotSeriesInput

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the plot series tool - hardcoded to CUUR0000SA0."""
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

        # Sort data chronologically (BLS returns newest first)
        data_list = []
        for point in data_points:
            year = point["year"]
            month = point["period"].replace("M", "").zfill(2)
            date_str = f"{year}-{month}"
            value = float(point["value"])
            data_list.append((date_str, value))

        # Sort oldest to newest
        data_list.sort()

        dates = [d[0] for d in data_list]
        values = [d[1] for d in data_list]

        # Create simple line plot
        plt.figure(figsize=(12, 6))
        plt.plot(values, linewidth=2, color='steelblue')
        plt.title('CPI All Urban Consumers: All Items', fontsize=14)
        plt.ylabel('Index Value', fontsize=12)
        plt.xlabel('Time', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        # Convert to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close()

        return {
            "status": "success",
            "series_id": series_id,
            "data_points": len(data_list),
            "date_range": f"{dates[0]} to {dates[-1]}",
            "image": {
                "format": "png",
                "encoding": "base64",
                "data": image_base64,
            },
        }
