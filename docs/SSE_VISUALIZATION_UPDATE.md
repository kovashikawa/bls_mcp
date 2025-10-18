# SSE Transport - Visualization Tool Integration

**Date**: October 18, 2025
**Update**: Added visualization tool to SSE/ngrok transport

## Summary

Successfully integrated the `plot_series` visualization tool into the SSE transport, making it available for remote access via ngrok. The SSE transport now dynamically includes all tools from the MCP server.

## Changes Made

### 1. Dynamic Tool Discovery

**Before:**
The SSE transport had a hardcoded list of 3 tools:
- get_series
- list_series
- get_series_info

**After:**
The SSE transport now dynamically reads all tools from the MCP server, including:
- get_series
- list_series
- get_series_info
- **plot_series** (NEW!)

### 2. Files Modified

#### [src/bls_mcp/transports/sse.py](../src/bls_mcp/transports/sse.py)

**Line 116-131: Dynamic tools/list handler**
```python
elif method == "tools/list":
    # Dynamically get tools from MCP server
    tools = []
    if hasattr(self.mcp_server, 'tools'):
        for tool_name, tool in self.mcp_server.tools.items():
            tools.append({
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.input_schema.model_json_schema()
            })

    response = {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {"tools": tools}
    }
```

**Line 34-54: Enhanced root endpoint**
```python
async def root_endpoint(request: Request) -> JSONResponse:
    """Root endpoint with server information."""
    # Get tool count dynamically
    tool_count = len(self.mcp_server.tools) if hasattr(self.mcp_server, 'tools') else 0
    tool_names = list(self.mcp_server.tools.keys()) if hasattr(self.mcp_server, 'tools') else []

    return JSONResponse({
        "name": "BLS MCP Server",
        "version": "1.18.0",
        "transport": "SSE",
        "endpoints": {
            "health": "/health",
            "mcp": "/mcp (POST only)",
            "sse": "/sse"
        },
        "tools": {
            "count": tool_count,
            "available": tool_names
        },
        "description": "Bureau of Labor Statistics data server via MCP protocol"
    })
```

### 3. New Test Script

Created [scripts/test_sse_viz.py](../scripts/test_sse_viz.py) to verify SSE integration:
- Tests that visualization tool is registered
- Simulates MCP tools/list request
- Validates tool schema

### 4. Documentation Updates

Updated [docs/VISUALIZATION.md](VISUALIZATION.md):
- Added section on remote access via ngrok
- Included curl examples for testing
- Documented SSE transport usage

## How It Works

### Architecture

```
MCP Client (Remote)
      ↓
   ngrok URL
      ↓
SSE Transport (HTTP/POST)
      ↓
BLSMCPServer.tools{}
      ↓
PlotSeriesTool.execute()
      ↓
Base64-encoded PNG
      ↓
JSON-RPC Response
      ↓
MCP Client (displays image)
```

### Tool Registration Flow

1. **Server Initialization** ([server.py](../src/bls_mcp/server.py))
   ```python
   if VISUALIZATION_AVAILABLE:
       self.tools["plot_series"] = PlotSeriesTool(self.data_provider)
   ```

2. **SSE Transport Startup** ([start_ngrok.py](../scripts/start_ngrok.py))
   ```python
   server = BLSMCPServer()  # Tools registered here
   sse_transport = SSETransport(server)  # Transport references server.tools
   ```

3. **Dynamic Tool Discovery** ([sse.py](../src/bls_mcp/transports/sse.py))
   ```python
   # When client calls tools/list
   for tool_name, tool in self.mcp_server.tools.items():
       tools.append({...})  # Includes plot_series!
   ```

## Testing

### Unit Test Results

```bash
uv run python scripts/test_sse_viz.py
```

**Output:**
```
✅ SUCCESS: Visualization tool is available via SSE transport!

📊 Visualization Tool Details:
  Name: plot_series
  Description: Create a simple static plot (line or bar chart)...
  Parameters:
    - series_id (required)
    - start_year (optional)
    - end_year (optional)
    - chart_type (optional)

🔧 Simulating MCP 'tools/list' request...
  Found 4 tools
    - get_series
    - list_series
    - get_series_info
    - plot_series
```

### Manual Testing

**1. Start ngrok server:**
```bash
cd /Users/rafaelkovashikawa/Downloads/projects/bls_food/bls_mcp
uv run python scripts/start_ngrok.py
```

**2. Check root endpoint:**
```bash
curl https://your-ngrok-url.ngrok-free.app/
```

**Response:**
```json
{
  "name": "BLS MCP Server",
  "version": "1.18.0",
  "transport": "SSE",
  "tools": {
    "count": 4,
    "available": [
      "get_series",
      "list_series",
      "get_series_info",
      "plot_series"
    ]
  }
}
```

**3. List tools via MCP:**
```bash
curl -X POST https://your-ngrok-url.ngrok-free.app/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list",
    "params": {}
  }'
```

**Response includes plot_series:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "tools": [
      {...},
      {
        "name": "plot_series",
        "description": "Create a simple static plot...",
        "inputSchema": {...}
      }
    ]
  }
}
```

**4. Call plot_series tool:**
```bash
curl -X POST https://your-ngrok-url.ngrok-free.app/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "plot_series",
      "arguments": {
        "series_id": "CUUR0000SA0",
        "start_year": 2023,
        "chart_type": "line"
      }
    }
  }'
```

**Response includes base64-encoded chart image.**

## Benefits

### 1. Scalability
- Adding new tools automatically includes them in SSE transport
- No need to manually update endpoint definitions
- Single source of truth (MCP server's tools dict)

### 2. Maintainability
- Reduces code duplication
- Tool schemas are always in sync
- Easier to add new tools in the future

### 3. Remote Access
- Visualization tool works via ngrok
- Can be accessed from any MCP client
- Enables multi-LLM testing

### 4. Consistency
- Same tools available in stdio and SSE transports
- Unified API across local and remote access
- Consistent behavior regardless of transport

## Usage Examples

### From Python Client

```python
import httpx
import json
import base64

async def get_chart():
    url = "https://your-ngrok-url.ngrok-free.app/mcp"

    # Call plot_series
    response = await httpx.post(url, json={
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "plot_series",
            "arguments": {
                "series_id": "CUUR0000SA0",
                "start_year": 2023,
                "chart_type": "line"
            }
        }
    })

    result = response.json()["result"]
    # Extract image data
    image_data = json.loads(result["content"][0]["text"])

    # Decode and save
    png_data = base64.b64decode(image_data["image"]["data"])
    with open("chart.png", "wb") as f:
        f.write(png_data)
```

### From MCP Inspector

```bash
# Install MCP Inspector
npm install -g @modelcontextprotocol/inspector

# Connect to ngrok URL
mcp-inspector --url https://your-ngrok-url.ngrok-free.app/mcp

# Use the UI to:
# 1. List tools (plot_series will appear)
# 2. Call plot_series with parameters
# 3. View the generated chart
```

## Compatibility

### Supported Transports
- ✅ stdio (local) - via server.py
- ✅ SSE (remote) - via sse.py + ngrok

### Supported Clients
- ✅ Claude Desktop (stdio)
- ✅ Any MCP client (SSE/HTTP)
- ✅ MCP Inspector
- ✅ Custom HTTP clients

## Known Limitations

1. **Image Size**: Large charts may increase response time
   - Current: 20-40KB per chart
   - Base64 encoding adds 33% overhead

2. **ngrok Free Tier**: URL changes on restart
   - Use ngrok paid plan for static URLs
   - Or use stdio for local development

3. **HTTP/SSE Only**: No WebSocket transport yet
   - Current SSE works well for most use cases
   - WebSocket could be added in future

## Future Enhancements

Potential improvements:
- [ ] WebSocket transport
- [ ] Image compression options
- [ ] Streaming for large charts
- [ ] Chart caching

## Related Documentation

- [VISUALIZATION.md](VISUALIZATION.md) - Complete visualization guide
- [PHASE2_VISUALIZATION_COMPLETE.md](PHASE2_VISUALIZATION_COMPLETE.md) - Original implementation
- [README.md](../README.md) - Project overview
- [CLAUDE_DESKTOP_SETUP.md](CLAUDE_DESKTOP_SETUP.md) - Local setup guide

## Conclusion

The visualization tool is now fully integrated into both stdio and SSE transports. The dynamic tool discovery ensures that any future tools will automatically be available via both transports without additional configuration.

### Key Achievements

✅ **Dynamic Tool Discovery**: SSE transport automatically includes all server tools
✅ **Visualization via ngrok**: Remote access to plot_series tool
✅ **Tested and Verified**: Test script confirms proper integration
✅ **Documented**: Complete usage examples and testing procedures

### Status

- **Implementation**: ✅ Complete
- **Testing**: ✅ Verified
- **Documentation**: ✅ Updated
- **Ready for Use**: ✅ Yes

---

**Last Updated**: October 18, 2025
**Next Steps**: Test with remote MCP clients, gather feedback
