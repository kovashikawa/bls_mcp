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
    async def test_plot_returns_minimal_data(self, plot_tool):
        """Test that plot_series returns minimal formatted data."""
        result = await plot_tool.execute({"series_id": "CUUR0000SA0"})

        assert result["series_id"] == "CUUR0000SA0"
        assert "data" in result
        assert "title" in result
        assert isinstance(result["data"], list)
        assert len(result["data"]) > 0

    @pytest.mark.asyncio
    async def test_minimal_data_format(self, plot_tool):
        """Test that data has minimal format with only date and value."""
        result = await plot_tool.execute({"series_id": "CUUR0000SA0"})

        # Check first data point has only required fields
        first_point = result["data"][0]
        assert "date" in first_point
        assert "value" in first_point

        # Should only have date and value fields (minimal)
        assert len(first_point.keys()) == 2

        # Verify data types
        assert isinstance(first_point["date"], str)
        assert isinstance(first_point["value"], (int, float))

        # Verify date format is YYYY-MM-DD
        date_parts = first_point["date"].split("-")
        assert len(date_parts) == 3
        assert len(date_parts[0]) == 4  # year
        assert len(date_parts[1]) == 2  # month
        assert len(date_parts[2]) == 2  # day

    @pytest.mark.asyncio
    async def test_has_required_fields(self, plot_tool):
        """Test that response has required fields."""
        result = await plot_tool.execute({"series_id": "CUUR0000SA0"})

        # Should have these fields
        assert "series_id" in result
        assert "title" in result
        assert "data" in result
        assert "instructions" in result

        # Should NOT have these fields (removed for minimal output)
        assert "status" not in result
        assert "statistics" not in result
        assert "date_range" not in result
        assert "series_title" not in result  # Changed to "title"

    @pytest.mark.asyncio
    async def test_data_sorted_chronologically(self, plot_tool):
        """Test that data is sorted from oldest to newest."""
        result = await plot_tool.execute({"series_id": "CUUR0000SA0"})

        dates = [point["date"] for point in result["data"]]

        # Verify dates are in ascending order
        for i in range(len(dates) - 1):
            assert dates[i] <= dates[i + 1], f"Dates not sorted: {dates[i]} should be <= {dates[i + 1]}"

    @pytest.mark.asyncio
    async def test_title_included(self, plot_tool):
        """Test that title is included."""
        result = await plot_tool.execute({"series_id": "CUUR0000SA0"})

        assert "title" in result
        assert isinstance(result["title"], str)
        # Title may be "CPI All Urban Consumers: All Items" or similar

    @pytest.mark.asyncio
    async def test_with_series_parameter(self, plot_tool):
        """Test that tool works with series_id parameter."""
        result = await plot_tool.execute({"series_id": "CUUR0000SA0"})

        assert result["series_id"] == "CUUR0000SA0"
        assert len(result["data"]) > 0

    @pytest.mark.asyncio
    async def test_with_year_range(self, plot_tool):
        """Test that tool works with year range parameters."""
        result = await plot_tool.execute({
            "series_id": "CUUR0000SA0",
            "start_year": 2020,
            "end_year": 2023
        })

        assert result["series_id"] == "CUUR0000SA0"
        assert len(result["data"]) > 0
        # Check dates are within range
        for point in result["data"]:
            year = int(point["date"][:4])
            assert 2020 <= year <= 2023

    @pytest.mark.asyncio
    async def test_all_values_are_numeric(self, plot_tool):
        """Test that all values are numeric."""
        result = await plot_tool.execute({"series_id": "CUUR0000SA0"})

        for point in result["data"]:
            assert isinstance(point["value"], (int, float))
            assert point["value"] > 0  # CPI values should be positive

    @pytest.mark.asyncio
    async def test_dates_are_first_of_month(self, plot_tool):
        """Test that all dates are first day of month (YYYY-MM-01)."""
        result = await plot_tool.execute({"series_id": "CUUR0000SA0"})

        for point in result["data"]:
            date_str = point["date"]
            # Should end with -01 (first day of month)
            assert date_str.endswith("-01"), f"Date {date_str} should be first of month"

    @pytest.mark.asyncio
    async def test_instructions_included(self, plot_tool):
        """Test that instructions are included to guide LLMs."""
        result = await plot_tool.execute({"series_id": "CUUR0000SA0"})

        assert "instructions" in result
        instructions = result["instructions"]

        # Should have usage guidelines
        assert "usage" in instructions
        assert isinstance(instructions["usage"], list)
        assert len(instructions["usage"]) > 0

        # Should have example code
        assert "example_python" in instructions
        assert "example_javascript" in instructions
        assert isinstance(instructions["example_python"], str)
        assert isinstance(instructions["example_javascript"], str)

        # Check key guidance is present
        usage_text = " ".join(instructions["usage"])
        assert "do not reconstruct" in usage_text.lower() or "use the data" in usage_text.lower()
        assert "sorted" in usage_text.lower()
        assert "do not truncate" in usage_text.lower()
