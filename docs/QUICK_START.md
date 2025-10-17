# Quick Start Guide - BLS MCP Server

Get up and running with the BLS MCP Server in 5 minutes!

## Prerequisites

- Python 3.10+ (tested with 3.13)
- pip or uv package manager
- Terminal/Command line access

## Installation

### 1. Navigate to the project

```bash
cd bls_mcp
```

### 2. Create virtual environment

```bash
python -m venv venv
```

### 3. Activate virtual environment

```bash
# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 4. Install the package

```bash
pip install -e .
```

### 5. Install dev dependencies (optional)

```bash
pip install pytest pytest-asyncio black ruff mypy
```

## Quick Test

### Test the MCP server

```bash
python scripts/test_mcp_client.py
```

Expected output:
```
🧪 Testing BLS MCP Server
============================================================
📤 Sending requests to MCP server...
📥 Responses received:
...
✅ Test completed successfully!
```

### Run unit tests

```bash
pytest tests/ -v
```

Expected output:
```
============================== 17 passed in 0.51s ==============================
```

## Usage Examples

### Example 1: List Available Series

**MCP Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "list_series",
    "arguments": {
      "limit": 5
    }
  }
}
```

**Response:**
Returns 5 CPI series with their metadata (titles, IDs, categories).

### Example 2: Get Series Data

**MCP Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "get_series",
    "arguments": {
      "series_id": "CUUR0000SA0",
      "start_year": 2023,
      "end_year": 2024
    }
  }
}
```

**Response:**
Returns 21 monthly data points for CPI All Items from 2023-2024.

### Example 3: Get Series Information

**MCP Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "get_series_info",
    "arguments": {
      "series_id": "CUUR0000SA0"
    }
  }
}
```

**Response:**
Returns complete metadata including title, area, item, and data availability.

## Available Series (Mock Data)

| Series ID | Description |
|-----------|-------------|
| CUUR0000SA0 | CPI All Items |
| CUUR0000SAF | CPI Food |
| CUUR0000SAF11 | CPI Food at Home |
| CUUR0000SETA | CPI Energy |
| CUUR0000SAH | CPI Housing |
| CUUR0000SETA01 | CPI Gasoline |
| CUUR0000SAT | CPI Transportation |
| CUUR0000SAM | CPI Medical Care |

All series have monthly data from 2020-2024.

## Configuration

### Environment Variables

Create a `.env` file (copy from `.env.example`):

```env
MCP_SERVER_PORT=3000
MCP_SERVER_HOST=localhost
LOG_LEVEL=INFO
DATA_PROVIDER=mock
```

### Logging Levels

- `DEBUG` - Detailed debugging information
- `INFO` - General information (default)
- `WARNING` - Warning messages
- `ERROR` - Error messages
- `CRITICAL` - Critical errors

## Integration with Claude Desktop

### Step 1: Create Claude Desktop Config

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "bls-data": {
      "command": "python",
      "args": [
        "/path/to/bls_mcp/scripts/start_server.py"
      ]
    }
  }
}
```

### Step 2: Restart Claude Desktop

Restart Claude Desktop to load the new MCP server.

### Step 3: Test in Claude

Try asking Claude:
- "List available BLS series"
- "Get CPI data for all items from 2023 to 2024"
- "Show me information about series CUUR0000SAF"

## Troubleshooting

### Issue: Module not found

**Solution:** Ensure you've activated the virtual environment and installed the package:
```bash
source venv/bin/activate
pip install -e .
```

### Issue: JSON decode error

**Solution:** The MCP protocol requires exact JSON-RPC format. Use the test client as a reference.

### Issue: Tests fail

**Solution:** Make sure pytest-asyncio is installed:
```bash
pip install pytest-asyncio
```

### Issue: Permission denied on scripts

**Solution:** Make scripts executable:
```bash
chmod +x scripts/*.py
```

## Development Workflow

### 1. Make changes to code

```bash
# Edit files in src/bls_mcp/
```

### 2. Run tests

```bash
pytest tests/ -v
```

### 3. Format code

```bash
black src/ tests/
```

### 4. Lint code

```bash
ruff check src/ tests/
```

### 5. Test MCP protocol

```bash
python scripts/test_mcp_client.py
```

## Next Steps

- Read [PLAN.md](../PLAN.md) for full project roadmap
- Read [PHASE1_COMPLETE.md](PHASE1_COMPLETE.md) for Phase 1 details
- Read [README.md](../README.md) for comprehensive documentation
- Explore [tools/](../src/bls_mcp/tools/) to see tool implementations
- Check [data/fixtures/](../src/bls_mcp/data/fixtures/) for mock data

## Getting Help

### Check logs

The server logs to stderr. Look for messages like:
```
2025-10-16 20:11:45 [INFO] bls_mcp.server: BLS MCP Server initialized successfully
```

### Debug mode

Set `LOG_LEVEL=DEBUG` in `.env` for detailed logging.

### Common MCP methods

- `initialize` - Initialize MCP connection
- `tools/list` - List available tools
- `tools/call` - Call a specific tool

## Performance Notes

- Mock data loads instantly (in-memory)
- stdio transport has minimal overhead
- All operations are async for efficiency
- Data is cached after first load

## Security Notes

- No authentication required for Phase 1
- stdio transport is local-only
- No network access needed
- Mock data is safe to share

---

Ready to move to Phase 2? Check out [PLAN.md](../PLAN.md) for ngrok integration and remote access!
