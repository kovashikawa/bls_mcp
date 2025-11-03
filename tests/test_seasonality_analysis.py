"""Tests for seasonality_analysis tool."""

import pytest

from bls_mcp.data.db_data_provider import DatabaseDataProvider
from bls_mcp.tools.seasonality_analysis import SeasonalityAnalysisTool

# Mark all tests in this file as integration tests (require database)
pytestmark = pytest.mark.integration


@pytest.fixture
def data_provider():
    """Create a database data provider."""
    try:
        return DatabaseDataProvider()
    except Exception as e:
        pytest.skip(f"Database not available: {e}")


@pytest.fixture
def seasonality_tool(data_provider):
    """Create a seasonality analysis tool."""
    return SeasonalityAnalysisTool(data_provider)


class TestSeasonalityAnalysisTool:
    """Test cases for SeasonalityAnalysisTool."""

    def test_tool_properties(self, seasonality_tool):
        """Test tool has correct properties."""
        assert seasonality_tool.name == "seasonality_analysis"
        assert "seasonality" in seasonality_tool.description.lower()
        assert seasonality_tool.input_schema is not None

    @pytest.mark.asyncio
    async def test_analyze_cpi_series(self, seasonality_tool):
        """Test seasonality analysis on CPI series."""
        result = await seasonality_tool.execute({"series_id": "CUUR0000SA0"})

        # Check main structure
        assert "series_id" in result
        assert "title" in result
        assert "latest_year_mom" in result
        assert "seasonal_patterns" in result
        assert "data_summary" in result

        # Should not have errors
        assert "error" not in result

    @pytest.mark.asyncio
    async def test_latest_year_mom_structure(self, seasonality_tool):
        """Test latest year MoM data structure."""
        result = await seasonality_tool.execute({"series_id": "CUUR0000SA0"})

        latest_year = result["latest_year_mom"]
        assert "year" in latest_year
        assert "months" in latest_year
        assert isinstance(latest_year["months"], list)
        assert len(latest_year["months"]) > 0

        # Check first month structure
        first_month = latest_year["months"][0]
        assert "month" in first_month
        assert "month_name" in first_month
        assert "mom_pct" in first_month
        assert "historical_median" in first_month
        assert "historical_mean" in first_month
        assert "percentile_rank" in first_month
        assert "vs_median" in first_month
        assert "vs_mean" in first_month
        assert "interpretation" in first_month

        # Should NOT have index value (removed for analytical focus)
        assert "value" not in first_month
        assert "mom_change" not in first_month

    @pytest.mark.asyncio
    async def test_seasonal_patterns_structure(self, seasonality_tool):
        """Test seasonal patterns data structure."""
        result = await seasonality_tool.execute({"series_id": "CUUR0000SA0"})

        patterns = result["seasonal_patterns"]
        assert isinstance(patterns, list)
        assert len(patterns) == 12  # One entry per month

        # Check each month has required fields
        for pattern in patterns:
            assert "month" in pattern
            assert "month_name" in pattern
            assert "sample_size" in pattern
            assert "mean" in pattern
            assert "median" in pattern
            assert "q25" in pattern
            assert "q75" in pattern
            assert "min" in pattern
            assert "max" in pattern

            # Verify month is in valid range
            assert 1 <= pattern["month"] <= 12

    @pytest.mark.asyncio
    async def test_data_summary(self, seasonality_tool):
        """Test data summary information."""
        result = await seasonality_tool.execute({"series_id": "CUUR0000SA0"})

        summary = result["data_summary"]
        assert "total_months" in summary
        assert "date_range" in summary
        assert "years_analyzed" in summary

        assert summary["total_months"] > 0
        assert summary["years_analyzed"] > 0
        assert "-" in summary["date_range"]  # Should have date format

    @pytest.mark.asyncio
    async def test_invalid_series_id(self, seasonality_tool):
        """Test with invalid series ID."""
        result = await seasonality_tool.execute({"series_id": "INVALID123"})

        assert "error" in result

    @pytest.mark.asyncio
    async def test_month_names_correct(self, seasonality_tool):
        """Test that month names are correct."""
        result = await seasonality_tool.execute({"series_id": "CUUR0000SA0"})

        patterns = result["seasonal_patterns"]
        expected_months = [
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

        for i, pattern in enumerate(patterns):
            assert pattern["month"] == i + 1
            assert pattern["month_name"] == expected_months[i]

    @pytest.mark.asyncio
    async def test_statistics_are_numeric(self, seasonality_tool):
        """Test that all statistics are numeric or None."""
        result = await seasonality_tool.execute({"series_id": "CUUR0000SA0"})

        patterns = result["seasonal_patterns"]
        for pattern in patterns:
            if pattern["sample_size"] > 0:
                # If we have data, statistics should be numeric
                assert isinstance(pattern["mean"], (int, float))
                assert isinstance(pattern["median"], (int, float))
                assert isinstance(pattern["q25"], (int, float))
                assert isinstance(pattern["q75"], (int, float))

    @pytest.mark.asyncio
    async def test_mom_percentages_reasonable(self, seasonality_tool):
        """Test that MoM percentages are in reasonable range."""
        result = await seasonality_tool.execute({"series_id": "CUUR0000SA0"})

        latest_year = result["latest_year_mom"]
        for month in latest_year["months"]:
            if month["mom_pct"] is not None:
                # CPI MoM changes should typically be small (< 5%)
                # But allow larger range for robustness
                assert -10 < month["mom_pct"] < 10, (
                    f"MoM % seems unreasonable: {month['mom_pct']} "
                    f"for {month['month_name']}"
                )

    @pytest.mark.asyncio
    async def test_quantile_positioning(self, seasonality_tool):
        """Test that quantile positioning is calculated correctly."""
        result = await seasonality_tool.execute({"series_id": "CUUR0000SA0"})

        latest_year = result["latest_year_mom"]
        for month in latest_year["months"]:
            # If we have MoM data, should have quantile info
            if month["mom_pct"] is not None:
                assert month["percentile_rank"] is not None
                assert month["vs_median"] is not None
                assert month["vs_mean"] is not None
                assert month["interpretation"] is not None

                # Percentile should be 0-100
                assert 0 <= month["percentile_rank"] <= 100

                # Interpretation should be valid
                valid_interpretations = [
                    "unusually_high",
                    "above_normal",
                    "normal",
                    "below_normal",
                    "unusually_low",
                    "insufficient_data",
                ]
                assert month["interpretation"] in valid_interpretations

    @pytest.mark.asyncio
    async def test_historical_comparison_present(self, seasonality_tool):
        """Test that historical comparisons are included."""
        result = await seasonality_tool.execute({"series_id": "CUUR0000SA0"})

        latest_year = result["latest_year_mom"]
        for month in latest_year["months"]:
            # Should have historical context
            assert "historical_median" in month
            assert "historical_mean" in month

            # If we have recent data, historical values should be present
            if month["mom_pct"] is not None:
                # For CPI which has long history, these should be numbers
                assert isinstance(month["historical_median"], (int, float, type(None)))
                assert isinstance(month["historical_mean"], (int, float, type(None)))
