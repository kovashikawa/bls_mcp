"""Tool for analyzing seasonality patterns in BLS time series data."""

from typing import Any, Dict, Optional

import numpy as np
from pydantic import BaseModel, Field

from ..utils.logger import get_logger
from ..utils.validators import validate_series_id
from .base import BaseTool

logger = get_logger(__name__)


class SeasonalityAnalysisInput(BaseModel):
    """Input schema for seasonality_analysis tool."""

    series_id: str = Field(
        description="BLS series ID to analyze (e.g., 'CUUR0000SA0' for CPI All Items)"
    )


class SeasonalityAnalysisTool(BaseTool):
    """Tool for analyzing seasonality patterns in BLS time series."""

    def __init__(self, data_provider: Any) -> None:
        """Initialize the seasonality analysis tool."""
        self.data_provider = data_provider

    @property
    def name(self) -> str:
        return "seasonality_analysis"

    @property
    def description(self) -> str:
        return (
            "Analyze seasonality patterns in BLS time series data. "
            "Returns month-over-month changes for the latest year and "
            "statistical measures (quantiles, average, median) for each month "
            "across the entire dataset."
        )

    @property
    def input_schema(self) -> type[BaseModel]:
        return SeasonalityAnalysisInput

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the seasonality analysis tool."""
        logger.info(f"Executing seasonality_analysis with arguments: {arguments}")

        # Validate input
        try:
            input_data = SeasonalityAnalysisInput(**arguments)
        except Exception as e:
            logger.error(f"Input validation failed: {e}")
            return {"error": f"Invalid input: {str(e)}"}

        # Validate series ID format
        if not validate_series_id(input_data.series_id):
            return {"error": f"Invalid series ID format: {input_data.series_id}"}

        # Fetch all data for this series
        try:
            series_data = await self.data_provider.get_series(
                series_id=input_data.series_id
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

        # Get metadata
        metadata = series_data.get("metadata", {})
        series_title = metadata.get("series_title") or f"Series {input_data.series_id}"

        # Parse and organize data
        monthly_data = self._parse_monthly_data(data_points)
        if not monthly_data:
            return {"error": "No monthly data available for analysis"}

        # Calculate seasonal patterns across all years (needed first for comparison)
        seasonal_patterns = self._calculate_seasonal_patterns(monthly_data)

        # Calculate MoM for latest year with quantile positioning
        latest_year_mom = self._calculate_latest_year_mom_with_quantiles(
            monthly_data, seasonal_patterns
        )

        logger.info(
            f"Successfully analyzed seasonality for {input_data.series_id} "
            f"({len(monthly_data)} months)"
        )

        return {
            "series_id": input_data.series_id,
            "title": series_title,
            "latest_year_mom": latest_year_mom,
            "seasonal_patterns": seasonal_patterns,
            "data_summary": {
                "total_months": len(monthly_data),
                "date_range": f"{monthly_data[0]['year']}-{monthly_data[0]['month']:02d} to "
                f"{monthly_data[-1]['year']}-{monthly_data[-1]['month']:02d}",
                "years_analyzed": len(set(d["year"] for d in monthly_data)),
            },
        }

    def _parse_monthly_data(
        self, data_points: list[Dict[str, Any]]
    ) -> list[Dict[str, Any]]:
        """
        Parse data points and extract monthly data.

        Args:
            data_points: Raw data points from provider

        Returns:
            List of dicts with year, month, and value
        """
        monthly_data = []

        for point in data_points:
            period = point.get("period", "")
            if not period.startswith("M"):
                # Skip non-monthly data (quarterly, annual, etc.)
                continue

            try:
                year = int(point["year"])
                month = int(period.replace("M", ""))
                value = float(point["value"])

                monthly_data.append({"year": year, "month": month, "value": value})
            except (ValueError, KeyError) as e:
                logger.warning(f"Skipping invalid data point: {e}")
                continue

        # Sort by year and month
        monthly_data.sort(key=lambda x: (x["year"], x["month"]))

        return monthly_data

    def _calculate_latest_year_mom_with_quantiles(
        self,
        monthly_data: list[Dict[str, Any]],
        seasonal_patterns: list[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Calculate month-over-month changes for the latest year with quantile positioning.

        Args:
            monthly_data: Sorted list of monthly data points
            seasonal_patterns: Pre-calculated seasonal patterns for comparison

        Returns:
            Dictionary with latest year MoM data and quantile positioning
        """
        if not monthly_data:
            return {"year": None, "months": []}

        # Get the latest year
        latest_year = monthly_data[-1]["year"]
        latest_year_data = [d for d in monthly_data if d["year"] == latest_year]

        mom_data = []
        for i, point in enumerate(latest_year_data):
            month_name = self._get_month_name(point["month"])

            if i == 0:
                # First month - try to get previous December
                prev_dec = next(
                    (
                        d
                        for d in reversed(monthly_data)
                        if d["year"] == latest_year - 1 and d["month"] == 12
                    ),
                    None,
                )
                if prev_dec:
                    mom_change = point["value"] - prev_dec["value"]
                    mom_pct = (mom_change / prev_dec["value"]) * 100
                else:
                    mom_change = None
                    mom_pct = None
            else:
                prev_point = latest_year_data[i - 1]
                mom_change = point["value"] - prev_point["value"]
                mom_pct = (mom_change / prev_point["value"]) * 100

            # Get historical pattern for this month
            pattern = next(
                (p for p in seasonal_patterns if p["month"] == point["month"]), None
            )

            # Calculate quantile positioning and interpretation
            if mom_pct is not None and pattern and pattern["mean"] is not None:
                quantile_info = self._get_quantile_position(mom_pct, pattern)
            else:
                quantile_info = {
                    "percentile": None,
                    "vs_median": None,
                    "vs_mean": None,
                    "interpretation": "insufficient_data",
                }

            mom_data.append(
                {
                    "month": point["month"],
                    "month_name": month_name,
                    "mom_pct": round(mom_pct, 3) if mom_pct is not None else None,
                    "historical_median": pattern["median"] if pattern else None,
                    "historical_mean": pattern["mean"] if pattern else None,
                    "percentile_rank": quantile_info["percentile"],
                    "vs_median": quantile_info["vs_median"],
                    "vs_mean": quantile_info["vs_mean"],
                    "interpretation": quantile_info["interpretation"],
                }
            )

        return {"year": latest_year, "months": mom_data}

    def _get_quantile_position(
        self, mom_pct: float, pattern: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Determine where current MoM falls in historical distribution.

        Args:
            mom_pct: Current month-over-month percentage
            pattern: Historical pattern with quantiles

        Returns:
            Dictionary with percentile rank and interpretation
        """
        q25 = pattern["q25"]
        median = pattern["median"]
        q75 = pattern["q75"]
        mean = pattern["mean"]
        min_val = pattern["min"]
        max_val = pattern["max"]

        # Calculate approximate percentile rank
        if mom_pct <= min_val:
            percentile = 0
        elif mom_pct >= max_val:
            percentile = 100
        elif mom_pct <= q25:
            # Between min and q25
            percentile = 25 * (mom_pct - min_val) / (q25 - min_val) if q25 != min_val else 0
        elif mom_pct <= median:
            # Between q25 and median
            percentile = 25 + 25 * (mom_pct - q25) / (median - q25) if median != q25 else 25
        elif mom_pct <= q75:
            # Between median and q75
            percentile = 50 + 25 * (mom_pct - median) / (q75 - median) if q75 != median else 50
        else:
            # Between q75 and max
            percentile = 75 + 25 * (mom_pct - q75) / (max_val - q75) if max_val != q75 else 75

        # Calculate differences from median and mean
        vs_median = round(mom_pct - median, 3)
        vs_mean = round(mom_pct - mean, 3)

        # Interpretation based on percentile
        if percentile >= 90:
            interpretation = "unusually_high"
        elif percentile >= 75:
            interpretation = "above_normal"
        elif percentile >= 25:
            interpretation = "normal"
        elif percentile >= 10:
            interpretation = "below_normal"
        else:
            interpretation = "unusually_low"

        return {
            "percentile": round(percentile, 1),
            "vs_median": vs_median,
            "vs_mean": vs_mean,
            "interpretation": interpretation,
        }

    def _calculate_seasonal_patterns(
        self, monthly_data: list[Dict[str, Any]]
    ) -> list[Dict[str, Any]]:
        """
        Calculate seasonal patterns (quantiles, avg, median) for each month.

        Args:
            monthly_data: Sorted list of monthly data points

        Returns:
            List of dicts with seasonal statistics for each month (1-12)
        """
        # Group MoM changes by month
        month_groups = {i: [] for i in range(1, 13)}

        # Calculate MoM changes for all data points
        for i in range(1, len(monthly_data)):
            current = monthly_data[i]
            previous = monthly_data[i - 1]

            # Only calculate MoM if consecutive months
            if (
                current["year"] == previous["year"]
                and current["month"] == previous["month"] + 1
            ) or (
                current["year"] == previous["year"] + 1
                and current["month"] == 1
                and previous["month"] == 12
            ):
                mom_pct = ((current["value"] - previous["value"]) / previous["value"]) * 100
                month_groups[current["month"]].append(mom_pct)

        # Calculate statistics for each month
        patterns = []
        for month in range(1, 13):
            changes = month_groups[month]
            month_name = self._get_month_name(month)

            if changes:
                patterns.append(
                    {
                        "month": month,
                        "month_name": month_name,
                        "sample_size": len(changes),
                        "mean": round(float(np.mean(changes)), 3),
                        "median": round(float(np.median(changes)), 3),
                        "q25": round(float(np.percentile(changes, 25)), 3),
                        "q75": round(float(np.percentile(changes, 75)), 3),
                        "min": round(float(np.min(changes)), 3),
                        "max": round(float(np.max(changes)), 3),
                    }
                )
            else:
                patterns.append(
                    {
                        "month": month,
                        "month_name": month_name,
                        "sample_size": 0,
                        "mean": None,
                        "median": None,
                        "q25": None,
                        "q75": None,
                        "min": None,
                        "max": None,
                    }
                )

        return patterns

    def _get_month_name(self, month: int) -> str:
        """Get month name from month number."""
        month_names = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]
        return month_names[month - 1] if 1 <= month <= 12 else "Unknown"
