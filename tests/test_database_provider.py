"""Integration tests for database data provider."""

import pytest

from bls_mcp.data.db_data_provider import DatabaseDataProvider

# Mark all tests in this file as integration tests
pytestmark = pytest.mark.integration


@pytest.fixture
def db_provider():
    """Create a database provider (requires database to be running)."""
    try:
        provider = DatabaseDataProvider()
        return provider
    except Exception as e:
        pytest.skip(f"Database not available: {e}")


class TestDatabaseDataProvider:
    """Integration tests for DatabaseDataProvider."""

    @pytest.mark.asyncio
    async def test_database_connection(self, db_provider):
        """Test that database connection works."""
        assert db_provider is not None
        assert db_provider._repository is not None
        assert db_provider._session is not None

    @pytest.mark.asyncio
    async def test_list_series(self, db_provider):
        """Test listing series from database."""
        # List all series (should have at least some)
        series_list = await db_provider.list_series(limit=10)
        assert isinstance(series_list, list)
        # Note: might be empty if database has no data

    @pytest.mark.asyncio
    async def test_list_series_with_category(self, db_provider):
        """Test listing series with category filter."""
        series_list = await db_provider.list_series(category="CPI", limit=5)
        assert isinstance(series_list, list)

    @pytest.mark.asyncio
    async def test_get_series_info(self, db_provider):
        """Test getting series info."""
        # This assumes CUUR0000SA0 exists in database
        try:
            info = await db_provider.get_series_info("CUUR0000SA0")
            assert info["series_id"] == "CUUR0000SA0"
            assert "data_point_count" in info
            assert "available_data" in info
            # Note: series_title might be None in database
            assert "series_title" in info
        except ValueError:
            pytest.skip("Series CUUR0000SA0 not found in database")

    @pytest.mark.asyncio
    async def test_get_series(self, db_provider):
        """Test getting series data."""
        try:
            series_data = await db_provider.get_series("CUUR0000SA0", start_year=2023)
            assert series_data["series_id"] == "CUUR0000SA0"
            assert "data" in series_data
            assert "metadata" in series_data
            assert "count" in series_data
            assert isinstance(series_data["data"], list)
        except ValueError:
            pytest.skip("Series CUUR0000SA0 not found in database")

    @pytest.mark.asyncio
    async def test_get_series_with_year_range(self, db_provider):
        """Test getting series data with year range."""
        try:
            series_data = await db_provider.get_series(
                "CUUR0000SA0", start_year=2023, end_year=2024
            )
            assert series_data["series_id"] == "CUUR0000SA0"

            # Verify all data points are within range
            for point in series_data["data"]:
                year = int(point["year"])
                assert 2023 <= year <= 2024
        except ValueError:
            pytest.skip("Series CUUR0000SA0 not found in database")

    @pytest.mark.asyncio
    async def test_get_series_invalid_id(self, db_provider):
        """Test that invalid series ID raises ValueError."""
        with pytest.raises(ValueError, match="not found"):
            await db_provider.get_series("INVALID_SERIES_ID")

    @pytest.mark.asyncio
    async def test_get_series_info_invalid_id(self, db_provider):
        """Test that invalid series ID raises ValueError for info."""
        with pytest.raises(ValueError, match="not found"):
            await db_provider.get_series_info("INVALID_SERIES_ID")
