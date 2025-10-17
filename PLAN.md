# BLS MCP Server - Project Plan

## Overview

A standalone MCP (Model Context Protocol) server for Bureau of Labor Statistics data, designed to work with multiple LLM clients through ngrok tunneling. This project is derived from `bls_data/` but focuses exclusively on MCP server functionality with mock data for initial iterations.

## Key Differences from bls_data

- **No FastMCP**: Uses official `mcp` Python SDK for full protocol control
- **HTTP Transport**: Uses SSE (Server-Sent Events) for remote access via ngrok
- **Mock Data First**: Initial implementation uses static/mock BLS data
- **Standalone**: Independent project with minimal dependencies
- **Multi-LLM Testing**: Designed to test with Claude, GPT-4, and other MCP-compatible LLMs

## Project Structure

```
bls_mcp/
├── README.md                    # Project documentation
├── PLAN.md                      # This file
├── pyproject.toml              # Package configuration
├── requirements.txt            # Dependencies
├── .env.example                # Environment variable template
├── .gitignore                  # Git ignore patterns
│
├── src/
│   └── bls_mcp/
│       ├── __init__.py
│       ├── server.py           # Main MCP server implementation
│       ├── transports/
│       │   ├── __init__.py
│       │   ├── stdio.py        # stdio transport for local testing
│       │   └── sse.py          # SSE transport for ngrok
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── base.py         # Base tool class
│       │   ├── get_series.py   # Get BLS series data
│       │   ├── search_series.py # Search series by keyword
│       │   ├── analyze_cpi.py  # CPI analysis tool
│       │   └── seasonality.py  # Seasonality analysis
│       ├── resources/
│       │   ├── __init__.py
│       │   └── series_catalog.py # BLS series catalog resource
│       ├── prompts/
│       │   ├── __init__.py
│       │   └── analysis_prompts.py # Pre-built analysis prompts
│       ├── data/
│       │   ├── __init__.py
│       │   ├── mock_data.py    # Mock BLS data generator
│       │   └── fixtures/
│       │       ├── cpi_series.json      # Mock CPI series data
│       │       ├── series_catalog.json  # Mock series catalog
│       │       └── historical_data.json # Mock historical data
│       └── utils/
│           ├── __init__.py
│           ├── logger.py       # Logging configuration
│           └── validators.py   # Input validation
│
├── tests/
│   ├── __init__.py
│   ├── test_server.py          # Server tests
│   ├── test_tools.py           # Tool tests
│   ├── test_transports.py      # Transport tests
│   └── fixtures/               # Test fixtures
│
├── scripts/
│   ├── start_server.py         # Start server (stdio mode)
│   ├── start_ngrok.py          # Start server with ngrok
│   ├── test_mcp_client.py      # Test MCP protocol
│   └── generate_mock_data.py   # Generate mock data
│
└── docs/
    ├── API.md                  # API documentation
    ├── TOOLS.md                # Tool reference
    ├── SETUP.md                # Setup guide
    └── TESTING.md              # Testing guide with multiple LLMs
```

## Phase 1: Foundation (Initial Iteration)

### Goals
- Set up project structure
- Implement basic MCP server with official SDK
- Create mock data system
- Support stdio transport for local testing

### Tasks

1. **Project Setup**
   - [ ] Create directory structure
   - [ ] Set up pyproject.toml with dependencies
   - [ ] Create .gitignore
   - [ ] Initialize git repository
   - [ ] Create README.md

2. **Core Server Implementation**
   - [ ] Implement base MCP server using official `mcp` SDK
   - [ ] Set up stdio transport
   - [ ] Implement server initialization and lifecycle
   - [ ] Add logging system

3. **Mock Data System**
   - [ ] Design mock data schema (following real BLS format)
   - [ ] Create JSON fixtures for CPI data
   - [ ] Implement mock data loader
   - [ ] Add data validation

4. **Basic Tools**
   - [ ] Implement `get_series` tool
   - [ ] Implement `list_series` tool
   - [ ] Implement `get_series_info` tool
   - [ ] Add tool registration system

5. **Testing**
   - [ ] Write unit tests for mock data
   - [ ] Write tests for basic tools
   - [ ] Create MCP protocol test client
   - [ ] Test stdio transport

### Dependencies (Phase 1)

```toml
dependencies = [
    "mcp>=1.0.0",                    # Official MCP SDK
    "pydantic>=2.5.0",               # Data validation
    "python-dotenv>=1.0.0",          # Environment variables
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
    "mypy>=1.0.0",
]
```

## Phase 2: HTTP Transport & ngrok Integration

### Goals
- Implement SSE (Server-Sent Events) transport
- Add ngrok integration for remote access
- Test with multiple LLM clients

### Tasks

1. **SSE Transport**
   - [ ] Implement SSE transport handler
   - [ ] Add CORS support
   - [ ] Implement connection management
   - [ ] Add authentication (optional)

2. **ngrok Integration**
   - [ ] Create ngrok startup script
   - [ ] Add ngrok configuration
   - [ ] Implement automatic URL detection
   - [ ] Add health check endpoint

3. **Multi-LLM Testing**
   - [ ] Test with Claude Desktop
   - [ ] Test with Claude API
   - [ ] Test with ChatGPT (if MCP support available)
   - [ ] Document client configurations

4. **Enhanced Tools**
   - [ ] Add image generation for visualizations
   - [ ] Implement seasonality analysis tool
   - [ ] Add comparison tools
   - [ ] Create aggregation tools

### Additional Dependencies (Phase 2)

```toml
dependencies = [
    # ... Phase 1 dependencies ...
    "uvicorn>=0.24.0",               # ASGI server
    "sse-starlette>=1.6.0",          # SSE support
    "pyngrok>=7.0.0",                # ngrok integration
    "matplotlib>=3.8.0",             # Visualization
    "numpy>=1.26.0",                 # Numerical operations
]
```

## Phase 3: Advanced Features

### Goals
- Implement MCP resources
- Add pre-built prompts
- Create advanced analysis tools
- Prepare for real data integration

### Tasks

1. **Resources**
   - [ ] Implement series catalog resource
   - [ ] Add historical data resource
   - [ ] Create documentation resource
   - [ ] Implement resource templates

2. **Prompts**
   - [ ] Create analysis prompt templates
   - [ ] Add comparison prompts
   - [ ] Implement custom prompt builder
   - [ ] Add prompt validation

3. **Advanced Analysis**
   - [ ] Implement trend analysis
   - [ ] Add forecast capabilities (simple models)
   - [ ] Create custom aggregations
   - [ ] Build comparison matrices

4. **Real Data Integration Path**
   - [ ] Design real data adapter interface
   - [ ] Create configuration for data source switching
   - [ ] Document migration from mock to real data
   - [ ] Add data caching layer

## Technical Architecture

### MCP Server Design

```python
# High-level server structure using official SDK

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.server.sse import sse_server
from mcp.types import Tool, Resource, Prompt

class BLSMCPServer:
    def __init__(self):
        self.server = Server("bls-mcp-server")
        self.data_provider = MockDataProvider()  # Switch to real later

    async def setup(self):
        # Register tools
        self.server.list_tools = self.handle_list_tools
        self.server.call_tool = self.handle_call_tool

        # Register resources
        self.server.list_resources = self.handle_list_resources
        self.server.read_resource = self.handle_read_resource

        # Register prompts
        self.server.list_prompts = self.handle_list_prompts
        self.server.get_prompt = self.handle_get_prompt

    async def run_stdio(self):
        async with stdio_server() as streams:
            await self.server.run(
                streams[0],
                streams[1],
                self.server.create_initialization_options()
            )

    async def run_sse(self, host: str, port: int):
        # SSE transport implementation
        pass
```

### Mock Data Design

```python
# Mock data follows real BLS API structure

{
    "series_id": "CUUR0000SA0",
    "series_title": "Consumer Price Index for All Urban Consumers: All Items",
    "survey_name": "Consumer Price Index",
    "area": "U.S. City Average",
    "item": "All Items",
    "seasonality": "Seasonally Adjusted",
    "data": [
        {
            "year": "2024",
            "period": "M01",
            "period_name": "January",
            "value": "308.417",
            "footnotes": []
        },
        // ... more data points
    ]
}
```

### Tool Design Pattern

```python
# Each tool follows a consistent pattern

from typing import Any, Dict
from pydantic import BaseModel, Field

class GetSeriesInput(BaseModel):
    series_id: str = Field(description="BLS series ID (e.g., 'CUUR0000SA0')")
    start_year: int | None = Field(default=None, description="Start year")
    end_year: int | None = Field(default=None, description="End year")

class GetSeriesTool:
    name = "get_series"
    description = "Fetch BLS data series by ID"
    input_schema = GetSeriesInput

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        # Validate input
        input_data = GetSeriesInput(**arguments)

        # Fetch data (from mock or real source)
        data = await self.data_provider.get_series(
            input_data.series_id,
            input_data.start_year,
            input_data.end_year
        )

        return {
            "series_id": input_data.series_id,
            "data": data,
            "metadata": {...}
        }
```

## ngrok Configuration

### Basic Setup

1. **Install ngrok**
   ```bash
   brew install ngrok  # macOS
   # or download from ngrok.com
   ```

2. **Configure authtoken**
   ```bash
   ngrok config add-authtoken YOUR_TOKEN
   ```

3. **Start server with ngrok**
   ```bash
   python scripts/start_ngrok.py
   ```

### Environment Variables

```env
# .env file
NGROK_AUTHTOKEN=your_token_here
MCP_SERVER_PORT=3000
MCP_SERVER_HOST=localhost
LOG_LEVEL=INFO
```

### ngrok Startup Script

```python
# scripts/start_ngrok.py

import asyncio
from pyngrok import ngrok
from bls_mcp.server import BLSMCPServer

async def main():
    # Start ngrok tunnel
    public_url = ngrok.connect(3000, bind_tls=True)
    print(f"🌐 MCP Server available at: {public_url}")

    # Start MCP server
    server = BLSMCPServer()
    await server.setup()
    await server.run_sse(host="localhost", port=3000)

if __name__ == "__main__":
    asyncio.run(main())
```

## Testing Strategy

### Local Testing (stdio)
```bash
# Test with stdio transport
python scripts/start_server.py

# Test with MCP client
python scripts/test_mcp_client.py
```

### Remote Testing (ngrok + SSE)
```bash
# Start server with ngrok
python scripts/start_ngrok.py

# Configure client with ngrok URL
# Test with different LLM clients
```

### Multi-LLM Client Testing

1. **Claude Desktop**
   - Configure in `claude_desktop_config.json`
   - Test stdio and SSE transports
   - Verify tool calls and responses

2. **Claude API**
   - Use Python MCP client
   - Test via API calls
   - Verify remote access through ngrok

3. **Other MCP Clients**
   - Test with official MCP inspector
   - Document compatibility
   - Create client configuration examples

## Mock Data Specifications

### Series Coverage
- **CPI Categories**: All Items, Food, Energy, Housing, Transportation
- **Time Range**: 2020-2024 (monthly data)
- **Geographies**: US City Average, Major metropolitan areas
- **Seasonal Adjustments**: Both seasonally adjusted and not adjusted

### Data Characteristics
- Realistic values based on actual BLS ranges
- Seasonal patterns in data
- Trend consistency
- Footnotes for special cases

## Success Criteria

### Phase 1 Complete
- [x] MCP server runs locally via stdio
- [x] Mock data system functional
- [x] Basic tools working (get_series, list_series, get_series_info)
- [x] Unit tests passing
- [x] Can be tested with MCP inspector

### Phase 2 Complete
- [x] SSE transport working
- [x] ngrok integration functional
- [x] Tested with at least 2 different LLM clients
- [x] Image generation working
- [x] Documentation complete

### Phase 3 Complete
- [x] Resources implemented
- [x] Prompts working
- [x] Advanced analysis tools functional
- [x] Clear path to real data integration

## Migration to Real Data (Future)

### Design Considerations
- Abstract data provider interface
- Environment-based configuration
- Separate mock and real implementations
- No changes to tool interfaces
- Transparent switching mechanism

### Implementation Pattern
```python
# Configurable data provider
class DataProviderFactory:
    @staticmethod
    def create(provider_type: str):
        if provider_type == "mock":
            return MockDataProvider()
        elif provider_type == "real":
            return RealBLSDataProvider()
        # ... other providers
```

## Development Workflow

1. **Setup**
   ```bash
   cd bls_mcp
   python -m venv venv
   source venv/bin/activate
   pip install -e ".[dev]"
   ```

2. **Development**
   ```bash
   # Run tests
   pytest

   # Format code
   black src/ tests/
   ruff check src/ tests/

   # Type checking
   mypy src/
   ```

3. **Testing**
   ```bash
   # Local (stdio)
   python scripts/start_server.py

   # Remote (ngrok)
   python scripts/start_ngrok.py
   ```

## Timeline Estimate

- **Phase 1**: 2-3 days (foundation + basic tools + mock data)
- **Phase 2**: 2-3 days (SSE transport + ngrok + multi-LLM testing)
- **Phase 3**: 3-4 days (resources + prompts + advanced features)

**Total**: ~7-10 days for complete implementation

## Open Questions

1. **Authentication**: Should we add authentication for ngrok endpoints?
2. **Rate Limiting**: Do we need rate limiting for the mock server?
3. **Caching**: Should we implement caching for mock data responses?
4. **Monitoring**: Do we want telemetry/monitoring in this version?
5. **Error Handling**: What level of error detail should we expose?

## Next Steps

1. Review and approve this plan
2. Create initial project structure
3. Begin Phase 1 implementation
4. Set up CI/CD (optional for initial version)
5. Create documentation templates
