"""Database data provider for BLS MCP server using bls_data PostgreSQL database."""

import os
import sys
from pathlib import Path
from typing import Any

from ..utils.logger import get_logger

logger = get_logger(__name__)


class DatabaseDataProvider:
    """
    Provides BLS data from PostgreSQL database using bls_data infrastructure.

    This provider connects to the bls_data PostgreSQL database and uses the
    existing repository pattern to fetch series data.
    """

    def __init__(self) -> None:
        """Initialize database data provider."""
        self._repository = None
        self._db_config = None
        self._session = None
        self._init_database()

    def _init_database(self) -> None:
        """Initialize database connection and repository."""
        try:
            # Add bls_data to Python path if not already there
            bls_data_path = Path(__file__).parent.parent.parent.parent.parent / "bls_data"
            if bls_data_path.exists() and str(bls_data_path) not in sys.path:
                sys.path.insert(0, str(bls_data_path))
                logger.info(f"Added bls_data path: {bls_data_path}")

            # Import bls_data modules
            from database.config import DatabaseConfig
            from database.repository import BLSDataRepository

            # Initialize database config
            self._db_config = DatabaseConfig()

            # Test connection
            if not self._db_config.check_connection():
                raise ConnectionError("Database connection failed")

            logger.info("Database connection successful")

            # Create session and repository
            self._session = self._db_config.SessionLocal()
            self._repository = BLSDataRepository(self._session)

            logger.info("DatabaseDataProvider initialized successfully")

        except ImportError as e:
            logger.error(f"Failed to import bls_data modules: {e}")
            raise ImportError(
                "Cannot import bls_data modules. Make sure bls_data is in the parent directory."
            ) from e
        except ConnectionError as e:
            logger.error(f"Database connection failed: {e}")
            raise ConnectionError(
                "Cannot connect to PostgreSQL database. "
                "Make sure the database is running and credentials are correct in .env"
            ) from e
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    async def get_series(
        self,
        series_id: str,
        start_year: int | None = None,
        end_year: int | None = None,
    ) -> dict[str, Any]:
        """
        Get data for a specific series from database.

        Args:
            series_id: BLS series ID (e.g., 'CUUR0000SA0')
            start_year: Optional start year filter
            end_year: Optional end year filter

        Returns:
            Dictionary with series data

        Raises:
            ValueError: If series not found
        """
        try:
            # Get series data from database using repository
            df = self._repository.get_series_data(
                series_ids=[series_id],
                start_year=start_year,
                end_year=end_year,
                include_metadata=True
            )

            if df.empty:
                raise ValueError(f"Series '{series_id}' not found in database")

            # Extract metadata from first row
            first_row = df.iloc[0]
            metadata = {
                "series_id": series_id,
                "series_title": first_row.get("series_title", ""),
                "survey_name": first_row.get("survey_name", ""),
                "area": first_row.get("area", ""),
                "item": first_row.get("item", ""),
                "seasonality": first_row.get("seasonality", ""),
            }

            # Convert data points to list of dicts (minimal format - no footnotes)
            data_points = []
            for _, row in df.iterrows():
                data_points.append({
                    "year": str(row["year"]),
                    "period": row["period"],
                    "period_name": row.get("period_name", ""),
                    "value": str(row["value"]) if row["value"] is not None else "",
                })

            logger.info(f"Retrieved {len(data_points)} data points for {series_id} from database")

            return {
                "series_id": series_id,
                "data": data_points,
                "metadata": metadata,
                "count": len(data_points),
            }

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error retrieving series {series_id}: {e}")
            raise ValueError(f"Failed to retrieve series data: {e}") from e

    async def list_series(
        self, category: str | None = None, limit: int = 50
    ) -> list[dict[str, Any]]:
        """
        List available series with optional filtering.

        Args:
            category: Optional category filter (e.g., 'CPI')
            limit: Maximum number of results

        Returns:
            List of series metadata dictionaries
        """
        try:
            from database.models import BLSSeries
            from sqlalchemy import func

            # Query series from database
            query = self._session.query(BLSSeries)

            # Filter by category if specified (match on survey_name or item)
            if category:
                category_upper = category.upper()
                query = query.filter(
                    (func.upper(BLSSeries.survey_name).contains(category_upper)) |
                    (func.upper(BLSSeries.item).contains(category_upper))
                )

            # Apply limit
            series_list = query.limit(limit).all()

            # Convert to list of dicts
            result = []
            for series in series_list:
                result.append({
                    "series_id": series.series_id,
                    "series_title": series.series_title or "",
                    "survey_name": series.survey_name or "",
                    "area": series.area or "",
                    "item": series.item or "",
                    "seasonality": series.seasonality or "",
                    "category": series.survey_name or "",
                })

            logger.info(f"Listed {len(result)} series from database")
            return result

        except Exception as e:
            logger.error(f"Error listing series: {e}")
            raise ValueError(f"Failed to list series: {e}") from e

    async def get_series_info(self, series_id: str) -> dict[str, Any]:
        """
        Get metadata information about a specific series.

        Args:
            series_id: BLS series ID

        Returns:
            Dictionary with series metadata

        Raises:
            ValueError: If series not found
        """
        try:
            from database.models import BLSSeries, BLSDataPoint
            from sqlalchemy import func

            # Query series from database
            series = self._session.query(BLSSeries).filter_by(series_id=series_id).first()

            if not series:
                raise ValueError(f"Series '{series_id}' not found")

            # Get data point count
            data_count = (
                self._session.query(func.count(BLSDataPoint.id))
                .filter_by(series_id=series_id)
                .scalar()
            )

            # Get freshness info
            freshness_info = self._repository.get_data_freshness([series_id])
            freshness = freshness_info.get(series_id, {})

            result = {
                "series_id": series.series_id,
                "series_title": series.series_title or "",
                "survey_name": series.survey_name or "",
                "measure_data_type": series.measure_data_type or "",
                "area": series.area or "",
                "item": series.item or "",
                "seasonality": series.seasonality or "",
                "base_period": series.base_period or "",
                "begin_year": series.begin_year,
                "begin_period": series.begin_period,
                "end_year": series.end_year,
                "end_period": series.end_period,
                "category": series.survey_name or "",
                "data_point_count": data_count,
                "available_data": data_count > 0,
                "last_updated": freshness.get("last_updated"),
                "last_extracted": freshness.get("last_extracted"),
            }

            logger.info(f"Retrieved info for {series_id} from database")
            return result

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error getting series info: {e}")
            raise ValueError(f"Failed to get series info: {e}") from e

    def __del__(self):
        """Cleanup database session on deletion."""
        if self._session:
            try:
                self._session.close()
                logger.debug("Database session closed")
            except Exception as e:
                logger.error(f"Error closing database session: {e}")
