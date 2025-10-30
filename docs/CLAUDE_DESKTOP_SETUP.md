# Claude Desktop Setup Guide - BLS MCP Server

Complete step-by-step guide for connecting the BLS MCP Server to Claude Desktop.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Setup Options](#setup-options)
3. [Option 1: UV with Shell Script (Recommended)](#option-1-uv-with-shell-script-recommended)
4. [Option 2: Direct Python Command](#option-2-direct-python-command)
5. [Option 3: Remote Access with ngrok](#option-3-remote-access-with-ngrok)
6. [Verification](#verification)
7. [Troubleshooting](#troubleshooting)
8. [Usage Examples](#usage-examples)

---

## Prerequisites

Before connecting to Claude Desktop, ensure you have:

1. **Claude Desktop installed**
   - Download from: https://claude.ai/download
   - Version: Latest (supports MCP protocol)

2. **BLS MCP Server installed**
   ```bash
   cd /Users/rafaelkovashikawa/Downloads/projects/bls_food/bls_mcp
   uv sync
   ```

3. **UV package manager** (recommended)
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

4. **Scripts are executable**
   ```bash
   chmod +x scripts/uv_start_server.sh
   chmod +x scripts/uv_test_client.sh
   chmod +x scripts/uv_test.sh
   ```

---

## Setup Options

There are three ways to connect the BLS MCP Server to Claude Desktop:

| Option | Transport | Best For | Complexity |
|--------|-----------|----------|------------|
| **Option 1** | stdio (shell script) | Local development | Easy |
| **Option 2** | stdio (direct Python) | Custom setups | Medium |
| **Option 3** | HTTP/SSE (ngrok) | Remote access, testing | Advanced |

---

## Option 1: UV with Shell Script (Recommended)

This is the **easiest and recommended** method for local development.

### Step 1: Locate Claude Desktop Config

The configuration file location depends on your OS:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

### Step 2: Create or Edit Config File

Open the config file in your editor:

```bash
# macOS
code ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Or use nano
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

### Step 3: Add BLS MCP Server Configuration

Add this configuration to the file:

```json
{
  "mcpServers": {
    "bls-data": {
      "command": "/Users/rafaelkovashikawa/Downloads/projects/bls_food/bls_mcp/scripts/uv_start_server.sh"
    }
  }
}
```

**Important Notes:**
- Use the **full absolute path** to the script
- The path must not contain `~` - use the full path as shown above
- Ensure the script is executable (`chmod +x`)

### Step 4: If You Have Other MCP Servers

If you already have other MCP servers configured, add the BLS server to the existing configuration:

```json
{
  "mcpServers": {
    "existing-server": {
      "command": "/path/to/existing/server"
    },
    "bls-data": {
      "command": "/Users/rafaelkovashikawa/Downloads/projects/bls_food/bls_mcp/scripts/uv_start_server.sh"
    }
  }
}
```

### Step 5: Restart Claude Desktop

1. **Quit Claude Desktop completely**
   - macOS: Cmd+Q or right-click dock icon → Quit
   - Make sure it's fully closed (check Activity Monitor if unsure)

2. **Relaunch Claude Desktop**
   - Open from Applications or Launchpad

### Step 6: Verify Connection

Once Claude Desktop restarts, you should see the BLS MCP Server tools available:

1. Look for a tools indicator in the chat interface
2. Type a message like: "What BLS data tools do you have?"
3. Claude should list the three tools: `get_series`, `list_series`, `get_series_info`

---

## Option 2: Direct Python Command

This option gives you more control over the Python environment.

### Configuration

```json
{
  "mcpServers": {
    "bls-data": {
      "command": "uv",
      "args": [
        "run",
        "python",
        "-m",
        "bls_mcp.server"
      ],
      "cwd": "/Users/rafaelkovashikawa/Downloads/projects/bls_food/bls_mcp"
    }
  }
}
```

**Notes:**
- `cwd` must be the project root directory
- UV will automatically activate the virtual environment
- More verbose logging available via environment variables

### With Environment Variables

```json
{
  "mcpServers": {
    "bls-data": {
      "command": "uv",
      "args": [
        "run",
        "python",
        "-m",
        "bls_mcp.server"
      ],
      "cwd": "/Users/rafaelkovashikawa/Downloads/projects/bls_food/bls_mcp",
      "env": {
        "LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

---

## Option 3: Remote Access with ngrok

This option allows remote access and testing from multiple LLMs.

### Step 1: Start ngrok Server

In a terminal:

```bash
cd /Users/rafaelkovashikawa/Downloads/projects/bls_food/bls_mcp
uv run python scripts/start_ngrok.py
```

You'll see output like:

```
🚀 Starting BLS MCP Server with ngrok tunnel
🌐 Creating ngrok tunnel for port 3000
✅ ngrok tunnel created successfully!
🔗 Public URL: https://xxxx-xxx-xxx-xxx.ngrok-free.app
📡 Local server: http://localhost:3000
```

### Step 2: Copy the Public URL

Copy the public URL from the output (e.g., `https://xxxx-xxx-xxx-xxx.ngrok-free.app`)

### Step 3: Configure Claude Desktop for HTTP

```json
{
  "mcpServers": {
    "bls-data": {
      "url": "https://xxxx-xxx-xxx-xxx.ngrok-free.app/mcp",
      "transport": "sse"
    }
  }
}
```

**Important:**
- Add `/mcp` to the end of the URL
- The ngrok server must be running while using Claude Desktop
- The URL changes each time you restart ngrok (unless you have a paid plan)

### Step 4: Keep Server Running

Keep the terminal window with the ngrok server open while using Claude Desktop.

---

## Verification

### Test the Connection

After restarting Claude Desktop, test the connection:

1. **Start a new conversation**

2. **Ask Claude about the tools:**
   ```
   What BLS data tools do you have available?
   ```

3. **Expected response:**
   Claude should mention three tools:
   - `get_series` - Fetch BLS time series data
   - `list_series` - List available series
   - `get_series_info` - Get series metadata

4. **Test a tool:**
   ```
   Can you list the available BLS series?
   ```

5. **Test with actual data:**
   ```
   Get the CPI data for series CUUR0000SA0 from 2023 to 2024
   ```

### Expected Tool Output

When tools are working correctly, you should see responses like:

**list_series:**
```json
{
  "series": [
    {
      "series_id": "CUUR0000SA0",
      "title": "All items in U.S. city average, all urban consumers, seasonally adjusted",
      "category": "cpi"
    },
    ...
  ],
  "count": 8
}
```

**get_series:**
```json
{
  "series_id": "CUUR0000SA0",
  "data": [
    {"year": "2023", "period": "M01", "value": "299.170"},
    {"year": "2023", "period": "M02", "value": "300.840"},
    ...
  ],
  "count": 21
}
```

---

## Troubleshooting

### Issue 1: Tools Not Appearing

**Symptoms:**
- Claude doesn't mention BLS tools
- No tools indicator in the interface

**Solutions:**

1. **Check config file syntax**
   ```bash
   # Validate JSON
   python -c "import json; json.load(open('$HOME/Library/Application Support/Claude/claude_desktop_config.json'))"
   ```

2. **Verify absolute path**
   ```bash
   # Test the path exists
   ls -la /Users/rafaelkovashikawa/Downloads/projects/bls_food/bls_mcp/scripts/uv_start_server.sh
   ```

3. **Check script permissions**
   ```bash
   chmod +x /Users/rafaelkovashikawa/Downloads/projects/bls_food/bls_mcp/scripts/uv_start_server.sh
   ```

4. **Fully quit and restart Claude Desktop**
   - Don't just close the window - use Cmd+Q
   - Check Activity Monitor to ensure it's closed

### Issue 2: Server Starts But Tools Don't Work

**Symptoms:**
- Tools appear but return errors
- Connection timeout errors

**Solutions:**

1. **Test server directly**
   ```bash
   cd /Users/rafaelkovashikawa/Downloads/projects/bls_food/bls_mcp
   ./scripts/uv_test_client.sh
   ```

2. **Check dependencies**
   ```bash
   cd /Users/rafaelkovashikawa/Downloads/projects/bls_food/bls_mcp
   uv sync
   ```

3. **View server logs**
   Add debug logging to config:
   ```json
   {
     "mcpServers": {
       "bls-data": {
         "command": "/Users/rafaelkovashikawa/Downloads/projects/bls_food/bls_mcp/scripts/uv_start_server.sh",
         "env": {
           "LOG_LEVEL": "DEBUG"
         }
       }
     }
   }
   ```

### Issue 3: UV Not Found

**Symptoms:**
- Error: "command not found: uv"
- Server doesn't start

**Solutions:**

1. **Install UV**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Add UV to PATH**
   ```bash
   # Add to ~/.zshrc or ~/.bashrc
   export PATH="$HOME/.cargo/bin:$PATH"
   ```

3. **Use full path to UV**
   ```bash
   which uv  # Get the full path
   ```

   Then update config with full path:
   ```json
   {
     "mcpServers": {
       "bls-data": {
         "command": "/Users/rafaelkovashikawa/.cargo/bin/uv",
         "args": ["run", "python", "-m", "bls_mcp.server"],
         "cwd": "/Users/rafaelkovashikawa/Downloads/projects/bls_food/bls_mcp"
       }
     }
   }
   ```

### Issue 4: ngrok URL Changes

**Symptoms:**
- Remote connection stops working
- Need to update config frequently

**Solutions:**

1. **Use ngrok paid plan** for static URLs
2. **Use stdio instead** for local development
3. **Create update script:**
   ```bash
   # scripts/update_ngrok_url.sh
   #!/bin/bash
   URL=$(curl -s http://localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url')
   echo "New ngrok URL: $URL/mcp"
   ```

### Issue 5: Permission Denied

**Symptoms:**
- Error: "Permission denied" when starting server

**Solutions:**

1. **Fix script permissions**
   ```bash
   chmod +x /Users/rafaelkovashikawa/Downloads/projects/bls_food/bls_mcp/scripts/*.sh
   ```

2. **Check directory permissions**
   ```bash
   ls -la /Users/rafaelkovashikawa/Downloads/projects/bls_food/bls_mcp
   ```

3. **Reinstall dependencies**
   ```bash
   cd /Users/rafaelkovashikawa/Downloads/projects/bls_food/bls_mcp
   rm -rf .venv
   uv sync
   ```

---

## Usage Examples

Once connected, you can ask Claude to use the BLS tools:

### Example 1: List Available Series

**You:**
```
What BLS data series are available?
```

**Claude will:**
- Call `list_series` tool
- Show you the 8 available CPI series
- Explain what each series measures

### Example 2: Get Specific Data

**You:**
```
Get the CPI data for "All items" (CUUR0000SA0) for 2023 and 2024
```

**Claude will:**
- Call `get_series` with series_id="CUUR0000SA0", start_year=2023, end_year=2024
- Show you the monthly data points
- Optionally analyze trends if you ask

### Example 3: Compare Series

**You:**
```
Compare food and energy CPI data for the last year
```

**Claude will:**
- Call `list_series` to find food and energy series
- Call `get_series` for each series
- Compare and analyze the data

### Example 4: Get Metadata

**You:**
```
What information do you have about series CUUR0000SA0?
```

**Claude will:**
- Call `get_series_info` with series_id="CUUR0000SA0"
- Show metadata (title, category, update frequency)
- Show data availability (year range)

---

## Configuration Reference

### Complete Configuration Example

```json
{
  "mcpServers": {
    "bls-data": {
      "command": "/Users/rafaelkovashikawa/Downloads/projects/bls_food/bls_mcp/scripts/uv_start_server.sh"
    }
  },
  "globalShortcut": "Ctrl+Shift+Space"
}
```

### Advanced Configuration with Multiple Servers

```json
{
  "mcpServers": {
    "bls-data": {
      "command": "/Users/rafaelkovashikawa/Downloads/projects/bls_food/bls_mcp/scripts/uv_start_server.sh",
      "env": {
        "LOG_LEVEL": "INFO",
        "DATA_PROVIDER": "mock"
      }
    },
    "another-server": {
      "command": "/path/to/another/server",
      "args": ["--port", "3001"]
    }
  }
}
```

### Environment Variables

Available environment variables for the BLS MCP Server:

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `DATA_PROVIDER` | `mock` | Data provider type (currently only "mock") |
| `MCP_SERVER_PORT` | `3000` | Port for SSE server (ngrok mode only) |
| `MCP_SERVER_HOST` | `localhost` | Host for SSE server (ngrok mode only) |

---

## Next Steps

After successful setup:

1. **Explore the data**
   - Ask Claude to list all series
   - Request data for different time periods
   - Compare multiple series

2. **Learn the tools**
   - Read `docs/QUICK_START.md` for detailed tool documentation
   - Check `docs/UV_USAGE.md` for advanced UV commands

3. **Phase 2 Features** (Coming Soon)
   - More analysis tools
   - Data visualization
   - Advanced filtering
   - Real BLS API integration

4. **Provide Feedback**
   - Report issues in the project repository
   - Suggest new features
   - Share use cases

---

## Support

### Documentation

- **Quick Start**: [docs/QUICK_START.md](QUICK_START.md)
- **UV Usage**: [docs/UV_USAGE.md](UV_USAGE.md)
- **Phase 1 Report**: [docs/PHASE1_FINAL_REPORT.md](PHASE1_FINAL_REPORT.md)
- **Project Plan**: [../PLAN.md](../PLAN.md)

### Testing

Test the server independently:

```bash
# Run unit tests
cd /Users/rafaelkovashikawa/Downloads/projects/bls_food/bls_mcp
./scripts/uv_test.sh

# Test MCP protocol
./scripts/uv_test_client.sh

# Start server manually
./scripts/uv_start_server.sh
```

### Common Questions

**Q: Can I use this without UV?**
A: Yes, but UV is highly recommended. See `README.md` for pip installation.

**Q: Does this work with the real BLS API?**
A: Not yet - Phase 1 uses mock data. Real API integration is planned for Phase 3.

**Q: Can I use this with other LLMs?**
A: Yes! Use the ngrok option (Option 3) for remote access from any MCP-compatible LLM.

**Q: How do I update the server?**
```bash
cd /Users/rafaelkovashikawa/Downloads/projects/bls_food/bls_mcp
git pull
uv sync
```

**Q: Can I run multiple instances?**
A: Yes, but each needs a unique server name in the config and different ports for ngrok mode.

---

**Status**: Production Ready
**Last Updated**: October 17, 2025
**Maintainer**: rafael
