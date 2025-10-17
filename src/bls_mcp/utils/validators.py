"""Input validation utilities for BLS MCP server."""

import re
from typing import Optional


def validate_series_id(series_id: str) -> bool:
    """
    Validate BLS series ID format.

    BLS series IDs are typically alphanumeric strings like:
    - CUUR0000SA0 (CPI series)
    - CES0000000001 (Employment series)

    Args:
        series_id: Series ID to validate

    Returns:
        True if valid, False otherwise
    """
    if not series_id:
        return False

    # Basic validation: 10-20 alphanumeric characters
    pattern = r"^[A-Z]{2,4}[A-Z0-9]{6,16}$"
    return bool(re.match(pattern, series_id.upper()))


def validate_year_range(
    start_year: Optional[int], end_year: Optional[int]
) -> tuple[bool, Optional[str]]:
    """
    Validate year range parameters.

    Args:
        start_year: Start year
        end_year: End year

    Returns:
        Tuple of (is_valid, error_message)
    """
    if start_year is not None:
        if start_year < 1900 or start_year > 2100:
            return False, "Start year must be between 1900 and 2100"

    if end_year is not None:
        if end_year < 1900 or end_year > 2100:
            return False, "End year must be between 1900 and 2100"

    if start_year is not None and end_year is not None:
        if start_year > end_year:
            return False, "Start year must be before or equal to end year"

    return True, None


def validate_limit(limit: int, max_limit: int = 1000) -> tuple[bool, Optional[str]]:
    """
    Validate limit parameter.

    Args:
        limit: Requested limit
        max_limit: Maximum allowed limit

    Returns:
        Tuple of (is_valid, error_message)
    """
    if limit < 1:
        return False, "Limit must be at least 1"

    if limit > max_limit:
        return False, f"Limit cannot exceed {max_limit}"

    return True, None
