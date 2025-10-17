# 🌐 BLS MCP Server - Remote Access with ngrok

## Current Status ✅

Your BLS MCP server is **currently running** and ready for remote access!

### Server Details
- **Status**: ✅ Active (PID: 69709)
- **Transport**: stdio (local) + SSE (remote via ngrok)
- **Data Provider**: Mock BLS data
- **Available Tools**: 
  - `get_series` - Fetch BLS data series
  - `list_series` - List available series  
  - `get_series_info` - Get series metadata

## 🚀 How to Start Remote Access

### Option 1: Quick Start (Recommended)
```bash
cd /Users/rafaelkovashikawa/Downloads/projects/bls_food/bls_mcp
uv run python scripts/start_ngrok.py
```

### Option 2: Using UV Script
```bash
cd /Users/rafaelkovashikawa/Downloads/projects/bls_food/bls_mcp
./scripts/uv_start_server.sh  # For local stdio access
```

## 🔧 ngrok Configuration

### Prerequisites ✅
- ✅ ngrok installed (`/opt/homebrew/bin/ngrok`)
- ✅ ngrok version 3.30.0
- ✅ Configuration file valid
- ✅ SSE dependencies installed

### Authentication Setup
If you haven't set up your ngrok authtoken yet:

1. **Get your authtoken** from [ngrok dashboard](https://dashboard.ngrok.com/get-started/setup/macos)
2. **Configure ngrok**:
   ```bash
   ngrok config add-authtoken YOUR_TOKEN_HERE
   ```

## 🌐 Remote Access URLs

When you start the server with ngrok, you'll see output like:
```
🌐 Public URL: https://abc123.ngrok.io
📡 Local server: http://localhost:3000
```

### Available Endpoints
- **Health Check**: `https://your-url.ngrok.io/health`
- **SSE Stream**: `https://your-url.ngrok.io/sse`
- **MCP API**: `https://your-url.ngrok.io/mcp` (POST)

## 🧪 Testing Remote Access

### 1. Health Check
```bash
curl https://your-url.ngrok.io/health
```

### 2. Test MCP Request
```bash
curl -X POST https://your-url.ngrok.io/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list",
    "params": {}
  }'
```

### 3. Test SSE Connection
```bash
curl -N https://your-url.ngrok.io/sse
```

## 🔄 Switching Between Local and Remote

### Local Access (stdio)
```bash
uv run python scripts/start_server.py
```
- Used by Claude Desktop
- Direct process communication
- No network access needed

### Remote Access (ngrok + SSE)
```bash
uv run python scripts/start_ngrok.py
```
- Public URL via ngrok tunnel
- HTTP/SSE transport
- Accessible from anywhere

## 🛠️ Troubleshooting

### Issue: ngrok tunnel fails
**Solution**: Check your authtoken
```bash
ngrok config check
ngrok config add-authtoken YOUR_TOKEN
```

### Issue: Port already in use
**Solution**: Change port in `.env` file
```env
MCP_SERVER_PORT=3001
```

### Issue: SSE transport errors
**Solution**: Reinstall SSE dependencies
```bash
uv sync --extra sse
```

## 📋 Environment Variables

Create `.env` file for configuration:
```env
MCP_SERVER_PORT=3000
MCP_SERVER_HOST=localhost
LOG_LEVEL=INFO
DATA_PROVIDER=mock
```

## 🎯 Next Steps

1. **Start ngrok server**: `uv run python scripts/start_ngrok.py`
2. **Copy the public URL** from the output
3. **Test the endpoints** using curl or browser
4. **Share the URL** with others for remote access

## 📚 Additional Resources

- [ngrok Documentation](https://ngrok.com/docs)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [BLS MCP Project Documentation](./README.md)

---

**Ready to go live?** Run `uv run python scripts/start_ngrok.py` and share your public URL! 🚀
