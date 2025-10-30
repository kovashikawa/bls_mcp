# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A standalone Model Context Protocol (MCP) server for Bureau of Labor Statistics (BLS) data. Built with the official `mcp` Python SDK, this server provides tools for accessing CPI (Consumer Price Index) data through mock data fixtures. Currently in Phase 2 with visualization capabilities.

## Key Architecture

### MCP Server Design

The server uses the official MCP SDK (not FastMCP) with:
- **stdio transport** for local testing and Claude Desktop integration
- **SSE transport** for remote access via ngrok
- **Tool-based architecture** where each tool inherits from `BaseTool`
- **Mock data provider** that loads from JSON fixtures on-demand with lazy loading

### Data Flow

```
MCP Client (Claude Desktop, etc.)
    ↓ JSON-RPC over stdio/SSE
BLSMCPServer (server.py)
    ↓ tool routing
Tool classes (get_series.py, plot_series.py, etc.)
    ↓ async data fetching
MockDataProvider (mock_data.py)
    ↓ lazy load from fixtures/
JSON fixtures (cpi_series.json, historical_data.json)
```

### Tool Pattern

All tools follow this pattern:
1. Inherit from `BaseTool` abstract class
2. Define `name`, `description`, and `input_schema` (Pydantic model)
3. Implement async `execute(arguments)` method
4. Return structured dict with `status` and data/error
5. Input validation happens via Pydantic before execution

### Critical Implementation Details

- **plot_series returns data, not images**: The tool returns structured JSON data suitable for client-side plotting, not pre-rendered images. This is more stable across different LLM clients (ChatGPT, Claude, etc.).
- **Lazy data loading**: Mock data loads from JSON fixtures only when first accessed and caches in memory
- **Multiple server entry points**: `bls-mcp` (stdio) and `bls-mcp-ngrok` (SSE) defined in pyproject.toml
- **No matplotlib dependency**: The plot_series tool no longer requires matplotlib - it just formats and returns data

## Development Commands

### Environment Setup

```bash
# Using UV (recommended - 10x faster)
uv sync                    # Install core dependencies
uv sync --all-extras       # Install all dependencies (dev, sse)

# Using pip (traditional)
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -e .
pip install -e ".[dev,sse]"  # With all extras
```

### Running the Server

```bash
# Local stdio mode (for Claude Desktop)
./scripts/uv_start_server.sh
# Or: uv run python scripts/start_server.py
# Or: python scripts/start_server.py

# SSE mode with ngrok (for remote access)
./start_public_server.sh
# Or: python scripts/start_ngrok.py
```

### Testing

```bash
# Run all tests
./scripts/uv_test.sh
# Or: uv run pytest
# Or: pytest

# Run specific test file
uv run pytest tests/test_tools.py
pytest tests/test_plot_series.py -v

# Run with coverage
pytest --cov=bls_mcp --cov-report=term

# Test MCP client interaction
./scripts/uv_test_client.sh
# Or: python scripts/test_mcp_client.py

# Test visualization (generates PNG files)
uv run python scripts/test_visualization.py
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint
ruff check src/ tests/

# Type checking
mypy src/
```

## Available Tools

### Phase 1 Tools (Data Access)
- **get_series**: Fetch BLS data series with optional year filtering
- **list_series**: List available series with optional category filter
- **get_series_info**: Get metadata about a specific series

### Phase 2 Tools (Data Formatting)
- **plot_series**: Return CPI All Items data formatted for client-side plotting (no parameters needed)

## Mock Data

Located in `src/bls_mcp/data/fixtures/`:
- **cpi_series.json**: Series catalog metadata (8 CPI series)
- **historical_data.json**: Time series data (2020-2024, monthly, 114 data points total)

Series available:
- CUUR0000SA0 (All Items)
- CUUR0000SAF (Food)
- CUUR0000SAF11 (Food at Home)
- CUUR0000SETA (Energy)
- CUUR0000SAH (Housing)
- CUUR0000SETA01 (Gasoline)
- CUUR0000SAT (Transportation)
- CUUR0000SAM (Medical Care)

## Adding New Tools

1. Create new file in `src/bls_mcp/tools/` (e.g., `my_tool.py`)
2. Inherit from `BaseTool` and implement:
   - `name` property (string)
   - `description` property (string)
   - `input_schema` property (Pydantic BaseModel subclass)
   - `async def execute(arguments)` method
3. Import and register in `server.py`:
   ```python
   from .tools.my_tool import MyTool
   self.tools["my_tool"] = MyTool(self.data_provider)
   ```
4. Add tests in `tests/test_tools.py` or separate test file
5. Update README.md with tool documentation

## Claude Desktop Integration

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "bls-data": {
      "command": "/path/to/bls_mcp/scripts/uv_start_server.sh"
    }
  }
}
```

Restart Claude Desktop to load the server. The tools will be available for Claude to use when discussing BLS data.

## Environment Variables

Create `.env` file (copy from `.env.example`):

```env
MCP_SERVER_PORT=3000
MCP_SERVER_HOST=localhost
LOG_LEVEL=INFO              # DEBUG, INFO, WARNING, ERROR, CRITICAL
DATA_PROVIDER=mock          # Currently only 'mock' supported
```

## Project Status

- **Phase 1**: Complete (stdio transport, basic tools, 17 tests)
- **Phase 2**: In progress (visualization tool complete, 26 tests total)
- **Phase 3**: Planned (MCP resources, prompts, real BLS API integration)

## Important Files

- `src/bls_mcp/server.py`: Main MCP server with tool registration
- `src/bls_mcp/tools/base.py`: Abstract base class for all tools
- `src/bls_mcp/data/mock_data.py`: Mock data provider with lazy loading
- `pyproject.toml`: Package config with optional dependency groups (dev, sse, viz)
- `scripts/uv_start_server.sh`: Startup script for Claude Desktop
- `tests/`: Unit tests for all components (26 tests, all passing)

## Common Patterns

### Async Tool Execution
All tool `execute()` methods are async and must be awaited. Data provider methods are also async.

### Error Handling
Tools return structured responses:
```python
# Success
{"status": "success", "data": [...], "count": 10}

# Error
{"status": "error", "error": "descriptive error message"}
```

### Optional Dependencies
Check if optional features are available before registering tools:
```python
try:
    from .tools.plot_series import PlotSeriesTool
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False
```

## Debugging

Set `LOG_LEVEL=DEBUG` in `.env` for detailed logging. Logs go to stderr and include:
- Tool calls and arguments
- Data provider operations
- Error stack traces
- MCP protocol messages

## Related Documentation

- `README.md`: Comprehensive project documentation
- `PLAN.md`: 3-phase project roadmap
- `docs/QUICK_START.md`: 5-minute setup guide
- `docs/VISUALIZATION.md`: Visualization tool guide
- `docs/UV_USAGE.md`: UV package manager guide
- `docs/CLAUDE_DESKTOP_SETUP.md`: Integration instructions
