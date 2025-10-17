# BLS MCP Server

A standalone MCP (Model Context Protocol) server for Bureau of Labor Statistics (BLS) data, designed to work with multiple LLM clients through both local and remote connections.

## Features

- **Official MCP SDK**: Built with the official `mcp` Python SDK for full protocol control
- **Mock Data First**: Uses realistic mock BLS data for rapid development and testing
- **Multiple Transports**: Supports both stdio (local) and SSE (remote via ngrok)
- **Multi-LLM Compatible**: Test with Claude, GPT-4, and other MCP-compatible clients
- **Modular Design**: Clean separation between tools, resources, and data providers

## Quick Start

### Installation

```bash
# Clone the repository
cd bls_mcp

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

# Or install with dev dependencies
pip install -e ".[dev]"
```

### Running the Server (Local)

```bash
# Start MCP server with stdio transport
python scripts/start_server.py
```

### Testing with MCP Inspector

```bash
# Install MCP inspector (if not already installed)
npm install -g @modelcontextprotocol/inspector

# Run inspector
mcp-inspector python scripts/start_server.py
```

## Project Status

**Current Phase**: Phase 1 - Foundation

- [x] Project structure created
- [x] Configuration files set up
- [ ] Mock data system implemented
- [ ] Core MCP server implemented
- [ ] Basic tools implemented
- [ ] Tests written

## Available Tools (Phase 1)

### `get_series`
Fetch BLS data series by ID with optional date range filtering.

**Parameters:**
- `series_id` (string, required): BLS series ID (e.g., "CUUR0000SA0")
- `start_year` (integer, optional): Start year for data range
- `end_year` (integer, optional): End year for data range

**Example:**
```json
{
  "name": "get_series",
  "arguments": {
    "series_id": "CUUR0000SA0",
    "start_year": 2020,
    "end_year": 2024
  }
}
```

### `list_series`
List available BLS series with optional filtering.

**Parameters:**
- `category` (string, optional): Filter by category (e.g., "CPI", "Employment")
- `limit` (integer, optional): Maximum number of results (default: 50)

### `get_series_info`
Get detailed metadata about a specific BLS series.

**Parameters:**
- `series_id` (string, required): BLS series ID

## Architecture

### Directory Structure

```
bls_mcp/
├── src/bls_mcp/
│   ├── server.py              # Main MCP server
│   ├── transports/
│   │   ├── stdio.py          # stdio transport (local)
│   │   └── sse.py            # SSE transport (remote - Phase 2)
│   ├── tools/
│   │   ├── base.py           # Base tool class
│   │   ├── get_series.py     # Get series tool
│   │   ├── list_series.py    # List series tool
│   │   └── get_series_info.py # Get series info tool
│   ├── data/
│   │   ├── mock_data.py      # Mock data provider
│   │   └── fixtures/         # JSON data fixtures
│   └── utils/
│       ├── logger.py         # Logging configuration
│       └── validators.py     # Input validation
├── tests/                     # Test suite
├── scripts/                   # Utility scripts
└── docs/                      # Documentation
```

### Data Flow

1. **Client Request** → MCP protocol (JSON-RPC)
2. **Transport Layer** → stdio or SSE
3. **Server Router** → Route to appropriate tool
4. **Tool Execution** → Fetch data from provider
5. **Data Provider** → Mock or real data source
6. **Response** → JSON formatted response

## Mock Data

The server uses realistic mock BLS data that follows the actual BLS API structure:

- **CPI Series**: Consumer Price Index data for various categories
- **Time Range**: 2020-2024 with monthly data points
- **Coverage**: Multiple categories (All Items, Food, Energy, Housing, etc.)
- **Realistic Values**: Based on actual BLS data patterns

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=bls_mcp

# Run specific test file
pytest tests/test_tools.py
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type checking
mypy src/
```

### Adding New Tools

1. Create tool file in `src/bls_mcp/tools/`
2. Implement tool class following the base pattern
3. Register tool in `server.py`
4. Add tests in `tests/test_tools.py`
5. Update documentation

## Roadmap

### Phase 1: Foundation (Current)
- [x] Project setup and configuration
- [ ] Mock data system
- [ ] Core MCP server with stdio transport
- [ ] Basic tools (get_series, list_series, get_series_info)
- [ ] Unit tests

### Phase 2: Remote Access
- [ ] SSE transport implementation
- [ ] ngrok integration
- [ ] Multi-LLM client testing
- [ ] Enhanced tools with visualization

### Phase 3: Advanced Features
- [ ] MCP resources (catalogs, documentation)
- [ ] Pre-built prompts for analysis
- [ ] Advanced analysis tools
- [ ] Migration path to real BLS data

## Configuration

Create a `.env` file (copy from `.env.example`):

```env
MCP_SERVER_PORT=3000
MCP_SERVER_HOST=localhost
LOG_LEVEL=INFO
DATA_PROVIDER=mock
```

## Contributing

This is a personal project, but suggestions and feedback are welcome!

## License

MIT License - see LICENSE file for details

## Related Projects

- [bls_data](../bls_data/) - Comprehensive BLS data toolkit (parent project)
- [Model Context Protocol](https://modelcontextprotocol.io/) - MCP specification and documentation

## Support

For issues or questions, please refer to the documentation in the `docs/` directory or check the PLAN.md file for development details.
