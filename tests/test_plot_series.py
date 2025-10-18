"""Tests for plot_series visualization tool."""

import base64
import pytest

from bls_mcp.data.mock_data import MockDataProvider
from bls_mcp.tools.plot_series import PlotSeriesTool


@pytest.fixture
def data_provider():
    """Create a mock data provider."""
    return MockDataProvider()


@pytest.fixture
def plot_tool(data_provider):
    """Create a plot series tool."""
    return PlotSeriesTool(data_provider)


class TestPlotSeriesTool:
    """Test cases for PlotSeriesTool."""

    def test_tool_properties(self, plot_tool):
        """Test tool has correct properties."""
        assert plot_tool.name == "plot_series"
        assert "plot" in plot_tool.description.lower()
        assert plot_tool.input_schema is not None

    @pytest.mark.asyncio
    async def test_plot_line_chart(self, plot_tool):
        """Test creating a line chart."""
        result = await plot_tool.execute({
            "series_id": "CUUR0000SA0",
            "start_year": 2023,
            "end_year": 2024,
            "chart_type": "line"
        })

        assert result["status"] == "success"
        assert result["series_id"] == "CUUR0000SA0"
        assert result["chart_type"] == "line"
        assert result["data_points"] > 0
        assert "image" in result
        assert result["image"]["format"] == "png"
        assert result["image"]["encoding"] == "base64"

        # Verify base64 data is valid
        image_data = result["image"]["data"]
        assert isinstance(image_data, str)
        assert len(image_data) > 0

        # Try to decode base64
        try:
            decoded = base64.b64decode(image_data)
            # Check PNG header
            assert decoded[:8] == b'\x89PNG\r\n\x1a\n'
        except Exception as e:
            pytest.fail(f"Failed to decode base64 image: {e}")

    @pytest.mark.asyncio
    async def test_plot_bar_chart(self, plot_tool):
        """Test creating a bar chart."""
        result = await plot_tool.execute({
            "series_id": "CUUR0000SA0",
            "chart_type": "bar"
        })

        assert result["status"] == "success"
        assert result["chart_type"] == "bar"
        assert "image" in result

    @pytest.mark.asyncio
    async def test_plot_with_date_range(self, plot_tool):
        """Test plotting with specific date range."""
        result = await plot_tool.execute({
            "series_id": "CUUR0000SA0",
            "start_year": 2023,
            "end_year": 2023
        })

        assert result["status"] == "success"
        assert "2023" in result["date_range"]["start"]
        assert "2023" in result["date_range"]["end"]

    @pytest.mark.asyncio
    async def test_plot_invalid_series(self, plot_tool):
        """Test plotting with invalid series ID."""
        result = await plot_tool.execute({
            "series_id": "INVALID123"
        })

        assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_plot_value_statistics(self, plot_tool):
        """Test that value statistics are included."""
        result = await plot_tool.execute({
            "series_id": "CUUR0000SA0"
        })

        assert result["status"] == "success"
        assert "value_range" in result
        assert "min" in result["value_range"]
        assert "max" in result["value_range"]
        assert "mean" in result["value_range"]

        # Verify statistics make sense
        assert result["value_range"]["min"] <= result["value_range"]["max"]
        assert result["value_range"]["min"] <= result["value_range"]["mean"] <= result["value_range"]["max"]

    @pytest.mark.asyncio
    async def test_plot_default_chart_type(self, plot_tool):
        """Test that default chart type is line."""
        result = await plot_tool.execute({
            "series_id": "CUUR0000SA0"
        })

        assert result["status"] == "success"
        assert result["chart_type"] == "line"

    @pytest.mark.asyncio
    async def test_plot_includes_metadata(self, plot_tool):
        """Test that plot includes series metadata."""
        result = await plot_tool.execute({
            "series_id": "CUUR0000SA0"
        })

        assert result["status"] == "success"
        assert "title" in result
        assert len(result["title"]) > 0
        assert result["series_id"] == "CUUR0000SA0"

    @pytest.mark.asyncio
    async def test_plot_invalid_input(self, plot_tool):
        """Test plotting with invalid input."""
        result = await plot_tool.execute({
            "chart_type": "invalid_type"
            # Missing required series_id
        })

        assert result["status"] == "error"
        assert "error" in result
