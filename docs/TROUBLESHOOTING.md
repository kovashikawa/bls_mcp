# Troubleshooting Guide - BLS MCP Server

This guide covers common issues when setting up the BLS MCP Server with Claude Desktop.

## Issue 1: `spawn uv ENOENT`

### Symptoms
```
Error: spawn uv ENOENT
Server disconnected
```

### Cause
Claude Desktop cannot find the `uv` command. UV is installed at `/Users/rafaelkovashikawa/.local/bin/uv` but Claude Desktop only searches these paths:
- `/usr/local/bin`
- `/opt/homebrew/bin`
- `/usr/bin`
- `/bin`
- `/usr/sbin`
- `/sbin`

### Solution 1: Use Shell Script (Recommended)

The shell scripts have been updated to use the full path to UV.

Update your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "bls-mcp": {
      "command": "/Users/rafaelkovashikawa/Downloads/projects/bls_food/bls_mcp/scripts/uv_start_server.sh"
    }
  }
}
```

### Solution 2: Use Full Path to UV

```json
{
  "mcpServers": {
    "bls-mcp": {
      "command": "/Users/rafaelkovashikawa/.local/bin/uv",
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

**Important**: This requires the package to be installed in editable mode:
```bash
cd /Users/rafaelkovashikawa/Downloads/projects/bls_food/bls_mcp
/Users/rafaelkovashikawa/.local/bin/uv pip install -e .
```

---

## Issue 2: `ModuleNotFoundError: No module named 'bls_mcp'`

### Symptoms
```
ModuleNotFoundError: No module named 'bls_mcp'
Server transport closed unexpectedly
```

### Cause
When using `python -m bls_mcp.server`, Python expects the package to be installed. The package is not installed in editable mode by default.

### Solution 1: Use Shell Script (Recommended)

The shell script uses `scripts/start_server.py` which manually adds the `src` directory to Python's path, so it doesn't require package installation.

```json
{
  "mcpServers": {
    "bls-mcp": {
      "command": "/Users/rafaelkovashikawa/Downloads/projects/bls_food/bls_mcp/scripts/uv_start_server.sh"
    }
  }
}
```

### Solution 2: Install Package in Editable Mode

```bash
cd /Users/rafaelkovashikawa/Downloads/projects/bls_food/bls_mcp
/Users/rafaelkovashikawa/.local/bin/uv pip install -e .
```

Then use this config:
```json
{
  "mcpServers": {
    "bls-mcp": {
      "command": "/Users/rafaelkovashikawa/.local/bin/uv",
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

---

## Issue 3: Incorrect `--directory` Usage

### Symptoms
Server starts but immediately crashes with no clear error.

### Cause
Using `--directory` with the scripts folder instead of the project root:

```json
// INCORRECT
{
  "mcpServers": {
    "bls-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/rafaelkovashikawa/Downloads/projects/bls_food/bls_mcp/scripts/",
        "run",
        "start_server.py"
      ]
    }
  }
}
```

### Solution

Use `cwd` for the project root, not `--directory` for scripts:

```json
// CORRECT
{
  "mcpServers": {
    "bls-mcp": {
      "command": "/Users/rafaelkovashikawa/.local/bin/uv",
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

Or use the shell script which handles paths correctly.

---

## Issue 4: Tools Not Appearing in Claude Desktop

### Symptoms
- Claude Desktop starts without errors
- No tools indicator appears
- Claude doesn't recognize BLS tools

### Diagnostic Steps

1. **Check the logs:**
   ```bash
   tail -f ~/Library/Logs/Claude/mcp-server-bls-mcp.log
   ```

2. **Look for success message:**
   ```
   Server started and connected successfully
   ```

3. **Check for errors:**
   - `spawn uv ENOENT` → See Issue 1
   - `ModuleNotFoundError` → See Issue 2
   - `Server transport closed` → Server crashed, check previous errors

### Solutions

1. **Verify config syntax:**
   ```bash
   python -c "import json; print(json.load(open('$HOME/Library/Application Support/Claude/claude_desktop_config.json')))"
   ```

2. **Test server manually:**
   ```bash
   cd /Users/rafaelkovashikawa/Downloads/projects/bls_food/bls_mcp
   ./scripts/uv_start_server.sh
   # Press Ctrl+C to stop
   ```

3. **Fully restart Claude Desktop:**
   - Quit completely (Cmd+Q)
   - Check Activity Monitor to ensure it's closed
   - Relaunch

---

## Issue 5: Permission Denied

### Symptoms
```
Permission denied: /Users/rafaelkovashikawa/Downloads/projects/bls_food/bls_mcp/scripts/uv_start_server.sh
```

### Solution

Make scripts executable:
```bash
chmod +x /Users/rafaelkovashikawa/Downloads/projects/bls_food/bls_mcp/scripts/*.sh
```

---

## Recommended Configuration

After troubleshooting, this is the **recommended working configuration**:

```json
{
  "mcpServers": {
    "bls-mcp": {
      "command": "/Users/rafaelkovashikawa/Downloads/projects/bls_food/bls_mcp/scripts/uv_start_server.sh"
    }
  }
}
```

**Why this works:**
- Shell script uses full path to UV (no PATH issues)
- Uses `start_server.py` which adds `src` to path (no installation required)
- Handles all path resolution automatically
- Easy to debug (can run script manually)

---

## Viewing Logs

### Real-time monitoring
```bash
tail -f ~/Library/Logs/Claude/mcp-server-bls-mcp.log
```

### View recent errors
```bash
tail -50 ~/Library/Logs/Claude/mcp-server-bls-mcp.log
```

### Check all MCP logs
```bash
tail -100 ~/Library/Logs/Claude/mcp.log
```

### Key log messages

**Success:**
```
Server started and connected successfully
```

**Common errors:**
```
spawn uv ENOENT                    → UV not found (Issue 1)
ModuleNotFoundError                → Package not installed (Issue 2)
Server transport closed            → Server crashed
```

---

## Testing Checklist

Before reporting issues, verify:

- [ ] UV is installed: `/Users/rafaelkovashikawa/.local/bin/uv --version`
- [ ] Scripts are executable: `ls -la scripts/*.sh`
- [ ] Config syntax is valid: JSON validation
- [ ] Server runs manually: `./scripts/uv_start_server.sh`
- [ ] Tests pass: `./scripts/uv_test.sh`
- [ ] Claude Desktop fully restarted: Check Activity Monitor
- [ ] Logs show "Server started and connected successfully"

---

## Getting Help

If issues persist after trying these solutions:

1. **Collect diagnostic information:**
   ```bash
   # UV version
   /Users/rafaelkovashikawa/.local/bin/uv --version

   # Python version
   /Users/rafaelkovashikawa/.local/bin/uv run python --version

   # Package info
   cd /Users/rafaelkovashikawa/Downloads/projects/bls_food/bls_mcp
   /Users/rafaelkovashikawa/.local/bin/uv pip list | grep bls

   # Recent logs
   tail -50 ~/Library/Logs/Claude/mcp-server-bls-mcp.log
   ```

2. **Test server independently:**
   ```bash
   cd /Users/rafaelkovashikawa/Downloads/projects/bls_food/bls_mcp
   ./scripts/uv_test_client.sh
   ```

3. **Check configuration:**
   ```bash
   cat "$HOME/Library/Application Support/Claude/claude_desktop_config.json"
   ```

---

**Last Updated**: October 17, 2025
**Status**: Production Ready
