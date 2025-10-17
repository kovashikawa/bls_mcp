"""Mock data provider for BLS MCP server."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class MockDataProvider:
    """Provides mock BLS data for testing and development."""

    def __init__(self) -> None:
        """Initialize mock data provider."""
        self.fixtures_dir = Path(__file__).parent / "fixtures"
        self._series_catalog: Optional[Dict[str, Any]] = None
        self._historical_data: Optional[Dict[str, Any]] = None

    def _load_series_catalog(self) -> Dict[str, Any]:
        """Load series catalog from JSON fixture."""
        if self._series_catalog is None:
            catalog_path = self.fixtures_dir / "cpi_series.json"
            with open(catalog_path, "r") as f:
                self._series_catalog = json.load(f)
        return self._series_catalog

    def _load_historical_data(self) -> Dict[str, Any]:
        """Load historical data from JSON fixture."""
        if self._historical_data is None:
            data_path = self.fixtures_dir / "historical_data.json"
            with open(data_path, "r") as f:
                self._historical_data = json.load(f)
        return self._historical_data

    async def get_series(
        self,
        series_id: str,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Get data for a specific series.

        Args:
            series_id: BLS series ID (e.g., 'CUUR0000SA0')
            start_year: Optional start year filter
            end_year: Optional end year filter

        Returns:
            Dictionary with series data

        Raises:
            ValueError: If series not found
        """
        historical = self._load_historical_data()

        if series_id not in historical:
            raise ValueError(f"Series '{series_id}' not found in mock data")

        series_data = historical[series_id]
        data_points = series_data["data"]

        # Filter by year range if specified
        if start_year is not None or end_year is not None:
            filtered_points = []
            for point in data_points:
                year = int(point["year"])
                if start_year and year < start_year:
                    continue
                if end_year and year > end_year:
                    continue
                filtered_points.append(point)
            data_points = filtered_points

        # Get series metadata
        catalog = self._load_series_catalog()
        metadata = next(
            (s for s in catalog["series"] if s["series_id"] == series_id), {}
        )

        return {
            "series_id": series_id,
            "data": data_points,
            "metadata": metadata,
            "count": len(data_points),
        }

    async def list_series(
        self, category: Optional[str] = None, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        List available series with optional filtering.

        Args:
            category: Optional category filter (e.g., 'CPI')
            limit: Maximum number of results

        Returns:
            List of series metadata dictionaries
        """
        catalog = self._load_series_catalog()
        series_list = catalog["series"]

        # Filter by category if specified
        if category:
            series_list = [
                s for s in series_list if s.get("category", "").upper() == category.upper()
            ]

        # Apply limit
        series_list = series_list[:limit]

        return series_list

    async def get_series_info(self, series_id: str) -> Dict[str, Any]:
        """
        Get metadata information about a specific series.

        Args:
            series_id: BLS series ID

        Returns:
            Dictionary with series metadata

        Raises:
            ValueError: If series not found
        """
        catalog = self._load_series_catalog()

        for series in catalog["series"]:
            if series["series_id"] == series_id:
                # Get data point count
                historical = self._load_historical_data()
                data_count = 0
                if series_id in historical:
                    data_count = len(historical[series_id]["data"])

                return {
                    **series,
                    "data_point_count": data_count,
                    "available_data": series_id in historical,
                }

        raise ValueError(f"Series '{series_id}' not found")

    async def search_series(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for series by title or description.

        Args:
            query: Search query string
            limit: Maximum number of results

        Returns:
            List of matching series
        """
        catalog = self._load_series_catalog()
        query_lower = query.lower()

        results = []
        for series in catalog["series"]:
            # Search in title and item fields
            title = series.get("series_title", "").lower()
            item = series.get("item", "").lower()

            if query_lower in title or query_lower in item:
                results.append(series)

            if len(results) >= limit:
                break

        return results
