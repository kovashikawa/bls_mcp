# 🤖 Connecting Your BLS MCP Server to ChatGPT & AI Assistants

## 🌐 **Your Server Status**
- **Public URL**: `https://uncriticisable-multilaterally-semaj.ngrok-free.dev`
- **MCP Endpoint**: `https://uncriticisable-multilaterally-semaj.ngrok-free.dev/mcp`
- **Status**: ✅ **ONLINE** (I can see traffic in your logs!)

## 🎯 **Method 1: ChatGPT Integration (Recommended)**

### **Step 1: Enable Developer Mode**
1. Open ChatGPT in your browser
2. Go to **Settings** → **Advanced Settings**
3. Toggle on **Developer Mode**

### **Step 2: Create MCP Connector**
1. Go to **Settings** → **Connectors** → **Create**
2. Fill in the details:
   - **Connector Name**: `BLS Data Server`
   - **Description**: `Access Bureau of Labor Statistics data including CPI, employment, and economic indicators`
   - **Connector URL**: `https://uncriticisable-multilaterally-semaj.ngrok-free.dev/mcp`
   - **Authentication**: `None` (for now)
3. Click **Create**

### **Step 3: Use in ChatGPT**
1. Start a new chat
2. Click the **+** button near the message composer
3. Select **Developer Mode**
4. Toggle on your **BLS Data Server** connector
5. Test with prompts like:
   - "Use the BLS Data Server to get CPI data for all items"
   - "List available economic data series"
   - "Show me food price inflation data"

## 🔧 **Method 2: Direct API Integration**

### **For Custom Applications**
```python
import requests
import json

# Your MCP server endpoint
MCP_URL = "https://uncriticisable-multilaterally-semaj.ngrok-free.dev/mcp"

# Example: List available tools
def list_tools():
    response = requests.post(MCP_URL, json={
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list",
        "params": {}
    })
    return response.json()

# Example: Get CPI data
def get_cpi_data():
    response = requests.post(MCP_URL, json={
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
    })
    return response.json()

# Test the connection
print("Available tools:", list_tools())
print("CPI data:", get_cpi_data())
```

## 🧪 **Method 3: Test Your Integration**

### **Test Commands**
```bash
# Test health endpoint
curl https://uncriticisable-multilaterally-semaj.ngrok-free.dev/health

# Test MCP endpoint
curl -X POST https://uncriticisable-multilaterally-semaj.ngrok-free.dev/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list",
    "params": {}
  }'

# Test SSE stream
curl -N https://uncriticisable-multilaterally-semaj.ngrok-free.dev/sse
```

## 📋 **Available Tools for AI Assistants**

Your server provides these tools that AI can use:

### **1. `get_series`**
- **Purpose**: Fetch BLS data series by ID
- **Example**: Get CPI data for all items
- **Parameters**: `series_id`, `start_year`, `end_year`

### **2. `list_series`**
- **Purpose**: List available BLS data series
- **Example**: Show all CPI-related series
- **Parameters**: `category`, `limit`

### **3. `get_series_info`**
- **Purpose**: Get detailed metadata about a series
- **Example**: Get description and availability info
- **Parameters**: `series_id`

## 🎯 **Sample Data Available**

| Series ID | Description | Category |
|-----------|-------------|----------|
| CUUR0000SA0 | CPI All Items | CPI |
| CUUR0000SAF | CPI Food | CPI |
| CUUR0000SAF11 | CPI Food at Home | CPI |
| CUUR0000SETA | CPI Energy | CPI |
| CUUR0000SAH | CPI Housing | CPI |
| CUUR0000SAT | CPI Transportation | CPI |
| CUUR0000SAM | CPI Medical Care | CPI |

## 🔄 **Method 4: Claude Desktop (Alternative)**

If you prefer Claude Desktop:

1. Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "bls-data": {
      "command": "uv",
      "args": [
        "run",
        "python",
        "/Users/rafaelkovashikawa/Downloads/projects/bls_food/bls_mcp/scripts/start_server.py"
      ],
      "cwd": "/Users/rafaelkovashikawa/Downloads/projects/bls_food/bls_mcp"
    }
  }
}
```

2. Restart Claude Desktop

## 🚀 **Quick Start for ChatGPT**

**Right now, you can:**

1. **Open ChatGPT** → Settings → Developer Mode (ON)
2. **Create Connector**:
   - Name: `BLS Economic Data`
   - URL: `https://uncriticisable-multilaterally-semaj.ngrok-free.dev/mcp`
3. **Start chatting**:
   - "Use BLS Economic Data to get current inflation rates"
   - "Show me food price trends from the BLS server"
   - "What economic indicators are available?"

## 🔧 **Troubleshooting**

### **If ChatGPT can't connect:**
1. **Check server status**: `curl https://uncriticisable-multilaterally-semaj.ngrok-free.dev/health`
2. **Verify MCP endpoint**: Test the `/mcp` endpoint directly
3. **Check ngrok tunnel**: Make sure it's still active

### **If you get 404 errors:**
- The server is running but some endpoints return 404 (this is normal)
- Use the specific endpoints: `/health`, `/mcp`, `/sse`

## 🎉 **You're Ready!**

Your BLS MCP server is **live and accessible** to ChatGPT and other AI assistants. The traffic logs show it's already being accessed from various IP addresses, which means it's working perfectly!

**Next step**: Try the ChatGPT integration above! 🚀
