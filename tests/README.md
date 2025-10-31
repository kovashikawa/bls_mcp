# Tests Directory

This directory contains both automated pytest tests and manual test scripts for the BLS MCP server.

## Test Types

### Unit Tests (pytest)
Automated tests that run without external dependencies:
- `test_mock_data.py` - Tests for mock data provider
- `test_tools.py` - Tests for MCP tools
- `test_plot_series.py` - Tests for plot_series tool

### Integration Tests (pytest)
Tests that require external resources (database):
- `test_database_provider.py` - Database integration tests (requires PostgreSQL)

### Manual Test Scripts
Standalone scripts for interactive testing:
- `manual_test_database.py` - Test database connection and operations
- `manual_test_plot_series.py` - Demo plot_series data formatting

## Running Tests

### Prerequisites

Install required dependencies:
```bash
# For all tests
uv sync --extra dev

# For database tests
uv sync --extra database

# Install everything
uv sync --all-extras
```

### Run Unit Tests

```bash
# Run all unit tests
uv run pytest

# Run specific test file
uv run pytest tests/test_tools.py

# Run with verbose output
uv run pytest -v

# Run with coverage
uv run pytest --cov=bls_mcp --cov-report=term
```

### Run Integration Tests

```bash
# Run only integration tests (requires database)
uv run pytest -m integration

# Skip integration tests
uv run pytest -m "not integration"
```

### Run Manual Tests

```bash
# Test database connection
uv run python tests/manual_test_database.py

# Demo plot_series data formatting
uv run python tests/manual_test_plot_series.py
```

## Test Markers

Tests can be marked with pytest markers:
- `@pytest.mark.integration` - Requires external resources (database)
- `@pytest.mark.slow` - Long-running tests

## Troubleshooting

### "No module named 'sqlalchemy'"

**Solution**: Install database dependencies
```bash
uv sync --extra database
```

### "Database connection failed"

**Solutions**:
1. Make sure PostgreSQL is running: `brew services start postgresql@14`
2. Check database exists: `psql -U postgres -l | grep bls_data`
3. Verify credentials in `.env` file

### "Series not found"

**Solution**: Populate the database
```bash
cd ../bls_data
./update_cpi_data.sh
```

## CI/CD

For continuous integration, use:
```bash
# Run unit tests only (no database required)
uv run pytest -m "not integration"
```

This ensures tests pass in environments without a PostgreSQL database.
