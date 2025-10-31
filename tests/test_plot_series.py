"""Tests for plot_series data formatting tool."""

import pytest

from bls_mcp.data.db_data_provider import DatabaseDataProvider
from bls_mcp.tools.plot_series import PlotSeriesTool

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
def plot_tool(data_provider):
    """Create a plot series tool."""
    return PlotSeriesTool(data_provider)


class TestPlotSeriesTool:
    """Test cases for PlotSeriesTool."""

    def test_tool_properties(self, plot_tool):
        """Test tool has correct properties."""
        assert plot_tool.name == "plot_series"
        assert "plot" in plot_tool.description.lower() or "data" in plot_tool.description.lower()
        assert plot_tool.input_schema is not None

    @pytest.mark.asyncio
    async def test_plot_returns_data(self, plot_tool):
        """Test that plot_series returns formatted data."""
        result = await plot_tool.execute({})

        assert result["status"] == "success"
        assert result["series_id"] == "CUUR0000SA0"
        assert "data" in result
        assert isinstance(result["data"], list)
        assert len(result["data"]) > 0

    @pytest.mark.asyncio
    async def test_data_format(self, plot_tool):
        """Test that data has correct format for plotting."""
        result = await plot_tool.execute({})

        assert result["status"] == "success"

        # Check first data point has required fields
        first_point = result["data"][0]
        assert "date" in first_point
        assert "value" in first_point
        assert "year" in first_point
        assert "month" in first_point
        assert "period" in first_point

        # Verify data types
        assert isinstance(first_point["date"], str)
        assert isinstance(first_point["value"], (int, float))
        assert isinstance(first_point["year"], str)

    @pytest.mark.asyncio
    async def test_statistics_included(self, plot_tool):
        """Test that statistics are included."""
        result = await plot_tool.execute({})

        assert result["status"] == "success"
        assert "statistics" in result

        stats = result["statistics"]
        assert "count" in stats
        assert "min" in stats
        assert "max" in stats
        assert "average" in stats

        # Verify statistics make sense
        assert stats["min"] <= stats["max"]
        assert stats["min"] <= stats["average"] <= stats["max"]
        assert stats["count"] == len(result["data"])

    @pytest.mark.asyncio
    async def test_date_range_included(self, plot_tool):
        """Test that date range is included."""
        result = await plot_tool.execute({})

        assert result["status"] == "success"
        assert "date_range" in result
        assert "start" in result["date_range"]
        assert "end" in result["date_range"]

        # Verify dates are in YYYY-MM format
        start = result["date_range"]["start"]
        end = result["date_range"]["end"]
        assert len(start.split("-")) == 2
        assert len(end.split("-")) == 2

    @pytest.mark.asyncio
    async def test_plot_instructions_included(self, plot_tool):
        """Test that plot instructions are included."""
        result = await plot_tool.execute({})

        assert result["status"] == "success"
        assert "plot_instructions" in result

        instructions = result["plot_instructions"]
        assert "chart_type" in instructions
        assert "x_axis" in instructions
        assert "y_axis" in instructions
        assert "title" in instructions
        assert "x_label" in instructions
        assert "y_label" in instructions

        # Verify instruction values
        assert instructions["chart_type"] == "line"
        assert instructions["x_axis"] == "date"
        assert instructions["y_axis"] == "value"

    @pytest.mark.asyncio
    async def test_data_sorted_chronologically(self, plot_tool):
        """Test that data is sorted from oldest to newest."""
        result = await plot_tool.execute({})

        assert result["status"] == "success"

        dates = [point["date"] for point in result["data"]]

        # Verify dates are in ascending order
        for i in range(len(dates) - 1):
            assert dates[i] <= dates[i + 1], f"Dates not sorted: {dates[i]} should be <= {dates[i + 1]}"

    @pytest.mark.asyncio
    async def test_series_title_included(self, plot_tool):
        """Test that series title is included (may be None in database)."""
        result = await plot_tool.execute({})

        assert result["status"] == "success"
        assert "series_title" in result
        # Series title may be None in database - that's okay
        if result["series_title"]:
            assert len(result["series_title"]) > 0

    @pytest.mark.asyncio
    async def test_no_parameters_required(self, plot_tool):
        """Test that tool works with no parameters."""
        result = await plot_tool.execute({})

        assert result["status"] == "success"
        assert result["series_id"] == "CUUR0000SA0"
