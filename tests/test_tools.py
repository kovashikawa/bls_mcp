"""Tests for MCP tools."""

import pytest

from bls_mcp.data.mock_data import MockDataProvider
from bls_mcp.tools.get_series import GetSeriesTool
from bls_mcp.tools.get_series_info import GetSeriesInfoTool
from bls_mcp.tools.list_series import ListSeriesTool


@pytest.fixture
def data_provider():
    """Create a mock data provider instance."""
    return MockDataProvider()


@pytest.fixture
def get_series_tool(data_provider):
    """Create get_series tool instance."""
    return GetSeriesTool(data_provider)


@pytest.fixture
def list_series_tool(data_provider):
    """Create list_series tool instance."""
    return ListSeriesTool(data_provider)


@pytest.fixture
def get_series_info_tool(data_provider):
    """Create get_series_info tool instance."""
    return GetSeriesInfoTool(data_provider)


def test_get_series_tool_properties(get_series_tool):
    """Test get_series tool properties."""
    assert get_series_tool.name == "get_series"
    assert get_series_tool.description
    assert get_series_tool.input_schema


@pytest.mark.asyncio
async def test_get_series_tool_execute(get_series_tool):
    """Test get_series tool execution."""
    result = await get_series_tool.execute({"series_id": "CUUR0000SA0"})

    assert "error" not in result
    assert result["series_id"] == "CUUR0000SA0"
    assert "data" in result


@pytest.mark.asyncio
async def test_get_series_tool_with_years(get_series_tool):
    """Test get_series tool with year range."""
    result = await get_series_tool.execute(
        {"series_id": "CUUR0000SA0", "start_year": 2023, "end_year": 2024}
    )

    assert "error" not in result
    assert result["series_id"] == "CUUR0000SA0"


@pytest.mark.asyncio
async def test_get_series_tool_invalid_id(get_series_tool):
    """Test get_series tool with invalid ID."""
    result = await get_series_tool.execute({"series_id": "INVALID"})

    assert "error" in result


def test_list_series_tool_properties(list_series_tool):
    """Test list_series tool properties."""
    assert list_series_tool.name == "list_series"
    assert list_series_tool.description
    assert list_series_tool.input_schema


@pytest.mark.asyncio
async def test_list_series_tool_execute(list_series_tool):
    """Test list_series tool execution."""
    result = await list_series_tool.execute({"limit": 5})

    assert "error" not in result
    assert "series" in result
    assert len(result["series"]) <= 5


def test_get_series_info_tool_properties(get_series_info_tool):
    """Test get_series_info tool properties."""
    assert get_series_info_tool.name == "get_series_info"
    assert get_series_info_tool.description
    assert get_series_info_tool.input_schema


@pytest.mark.asyncio
async def test_get_series_info_tool_execute(get_series_info_tool):
    """Test get_series_info tool execution."""
    result = await get_series_info_tool.execute({"series_id": "CUUR0000SA0"})

    assert "error" not in result
    assert result["series_id"] == "CUUR0000SA0"
    assert "series_title" in result
