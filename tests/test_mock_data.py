"""Tests for mock data provider."""

import pytest

from bls_mcp.data.mock_data import MockDataProvider


@pytest.fixture
def data_provider():
    """Create a mock data provider instance."""
    return MockDataProvider()


@pytest.mark.asyncio
async def test_get_series(data_provider):
    """Test getting a series."""
    result = await data_provider.get_series("CUUR0000SA0")

    assert result["series_id"] == "CUUR0000SA0"
    assert "data" in result
    assert "metadata" in result
    assert result["count"] > 0


@pytest.mark.asyncio
async def test_get_series_with_year_filter(data_provider):
    """Test getting a series with year filtering."""
    result = await data_provider.get_series(
        "CUUR0000SA0", start_year=2023, end_year=2024
    )

    assert result["series_id"] == "CUUR0000SA0"
    assert all(2023 <= int(point["year"]) <= 2024 for point in result["data"])


@pytest.mark.asyncio
async def test_get_series_not_found(data_provider):
    """Test getting a non-existent series."""
    with pytest.raises(ValueError, match="not found"):
        await data_provider.get_series("INVALID_SERIES")


@pytest.mark.asyncio
async def test_list_series(data_provider):
    """Test listing series."""
    result = await data_provider.list_series()

    assert isinstance(result, list)
    assert len(result) > 0
    assert all("series_id" in series for series in result)


@pytest.mark.asyncio
async def test_list_series_with_category(data_provider):
    """Test listing series with category filter."""
    result = await data_provider.list_series(category="CPI")

    assert isinstance(result, list)
    assert all(series.get("category") == "CPI" for series in result)


@pytest.mark.asyncio
async def test_list_series_with_limit(data_provider):
    """Test listing series with limit."""
    result = await data_provider.list_series(limit=3)

    assert len(result) <= 3


@pytest.mark.asyncio
async def test_get_series_info(data_provider):
    """Test getting series info."""
    result = await data_provider.get_series_info("CUUR0000SA0")

    assert result["series_id"] == "CUUR0000SA0"
    assert "series_title" in result
    assert "data_point_count" in result
    assert result["available_data"] is True


@pytest.mark.asyncio
async def test_get_series_info_not_found(data_provider):
    """Test getting info for non-existent series."""
    with pytest.raises(ValueError, match="not found"):
        await data_provider.get_series_info("INVALID_SERIES")


@pytest.mark.asyncio
async def test_search_series(data_provider):
    """Test searching series."""
    result = await data_provider.search_series("Food")

    assert isinstance(result, list)
    assert len(result) > 0
    assert all("Food" in series["series_title"] or "Food" in series["item"] for series in result)
