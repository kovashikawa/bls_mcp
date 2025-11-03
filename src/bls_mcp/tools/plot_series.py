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
        seasonality = metadata.get("seasonality", "")

        # Calculate data quality metrics
        data_quality = self._calculate_data_quality(
            plot_data, data_points, seasonality
        )

        logger.info(
            f"Successfully formatted {len(plot_data)} data points for {input_data.series_id}"
        )

        return {
            "series_id": input_data.series_id,
            "title": series_title,
            "data": plot_data,
            "data_quality": data_quality,
            "instructions": {
                "usage": [
                    "Use the data array as returned. do not make any changes.",
                    "Do not truncate the series - plot all dates available in the response",
                    "Show exact Python/JavaScript that converts this JSON to a plot",
                    "For time series: use date as x-axis, value as y-axis",
                    "Do not fabricate monthly values - use only what comes from this response"
                ],
                "example_python": "import pandas as pd\nimport matplotlib.pyplot as plt\n\ndf = pd.DataFrame(data['data'])\ndf['date'] = pd.to_datetime(df['date'])\ndf = df.sort_values('date')\n\nplt.figure(figsize=(12, 6))\nplt.plot(df['date'], df['value'])\nplt.title(data['title'])\nplt.xlabel('Date')\nplt.ylabel('Index Value')\nplt.xticks(rotation=45)\nplt.tight_layout()\nplt.show()",
                "example_javascript": "const data = response.data;\nconst dates = data.map(d => d.date);\nconst values = data.map(d => d.value);\n\nnew Chart(ctx, {\n  type: 'line',\n  data: {\n    labels: dates,\n    datasets: [{\n      label: response.title,\n      data: values\n    }]\n  }\n});"
            }
        }

    def _calculate_data_quality(
        self,
        plot_data: list[Dict[str, Any]],
        raw_data_points: list[Dict[str, Any]],
        seasonality: str,
    ) -> Dict[str, Any]:
        """
        Calculate data quality metrics.

        Args:
            plot_data: Formatted plot data with dates and values
            raw_data_points: Raw data points from provider
            seasonality: Seasonality code (e.g., 'S' for seasonally adjusted)

        Returns:
            Dictionary with data quality metrics
        """
        if not plot_data:
            return {
                "has_gaps": False,
                "data_points": 0,
                "date_range": "N/A",
                "frequency": "unknown",
                "notes": "No data available",
            }

        # Detect frequency from period codes
        periods = [p.get("period", "") for p in raw_data_points]
        if all(p.startswith("M") for p in periods if p):
            frequency = "monthly"
        elif all(p.startswith("Q") for p in periods if p):
            frequency = "quarterly"
        elif all(p.startswith("A") or p.startswith("S") for p in periods if p):
            frequency = "annual"
        else:
            frequency = "mixed"

        # Detect gaps in the data
        has_gaps = self._detect_gaps(plot_data, frequency)

        # Format date range
        first_date = plot_data[0]["date"]
        last_date = plot_data[-1]["date"]
        # Convert YYYY-MM-DD to YYYY-MM format for display
        first_display = first_date[:7]  # YYYY-MM
        last_display = last_date[:7]
        date_range = f"{first_display} to {last_display}"

        # Generate notes based on seasonality
        notes = []
        if seasonality and "S" in seasonality.upper():
            notes.append("Seasonally adjusted")
        elif seasonality and "U" in seasonality.upper():
            notes.append("Not seasonally adjusted - expect seasonal patterns")
        else:
            notes.append("Not seasonally adjusted - expect monthly volatility")

        if has_gaps:
            notes.append("Data contains gaps")

        notes_text = "; ".join(notes) if notes else "No special notes"

        return {
            "has_gaps": has_gaps,
            "data_points": len(plot_data),
            "date_range": date_range,
            "frequency": frequency,
            "notes": notes_text,
        }

    def _detect_gaps(self, plot_data: list[Dict[str, Any]], frequency: str) -> bool:
        """
        Detect if there are gaps in the time series.

        Args:
            plot_data: Formatted plot data with dates
            frequency: Data frequency (monthly, quarterly, annual)

        Returns:
            True if gaps detected, False otherwise
        """
        if len(plot_data) < 2:
            return False

        from datetime import datetime
        from dateutil.relativedelta import relativedelta

        dates = [datetime.strptime(p["date"], "%Y-%m-%d") for p in plot_data]

        # Expected delta based on frequency
        if frequency == "monthly":
            expected_delta = relativedelta(months=1)
        elif frequency == "quarterly":
            expected_delta = relativedelta(months=3)
        elif frequency == "annual":
            expected_delta = relativedelta(years=1)
        else:
            # Can't detect gaps for mixed frequency
            return False

        # Check for gaps
        for i in range(len(dates) - 1):
            expected_next = dates[i] + expected_delta
            actual_next = dates[i + 1]

            # Allow for slight variation (e.g., 28-31 days for monthly)
            if frequency == "monthly":
                delta_days = abs((actual_next - expected_next).days)
                if delta_days > 5:  # More than 5 days difference
                    return True
            else:
                if actual_next != expected_next:
                    return True

        return False
