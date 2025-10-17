# Using BLS MCP Server with UV

This guide explains how to use the BLS MCP server with `uv`, the fast Python package installer and resolver.

## Why UV?

- **Faster**: 10-100x faster than pip
- **Better dependency resolution**: More reliable than pip
- **Lock files**: `uv.lock` ensures reproducible environments
- **Better for development**: Streamlined workflow

## Prerequisites

### Install UV

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with pip
pip install uv

# Or with Homebrew
brew install uv
```

Verify installation:
```bash
uv --version
# Should show: uv 0.8.x or higher
```

## Quick Start with UV

### 1. Clone and Navigate

```bash
cd bls_mcp
```

### 2. Sync Dependencies

```bash
# Install all dependencies (creates .venv automatically)
uv sync

# Or install with dev dependencies
uv sync --all-extras
```

That's it! `uv` automatically:
- Creates a `.venv` virtual environment
- Installs all dependencies from `pyproject.toml`
- Creates/updates `uv.lock` for reproducibility

### 3. Run the Server

```bash
# Using the convenience script
./scripts/uv_start_server.sh

# Or directly with uv
uv run python scripts/start_server.py

# Or using the installed command
uv run bls-mcp
```

### 4. Test the Server

```bash
# Run the test client
./scripts/uv_test_client.sh

# Or directly
uv run python scripts/test_mcp_client.py
```

### 5. Run Tests

```bash
# Run all tests
./scripts/uv_test.sh

# Or directly with uv
uv run pytest tests/ -v

# With coverage
uv run pytest tests/ --cov=bls_mcp
```

## UV Commands Reference

### Dependency Management

```bash
# Sync dependencies (install/update)
uv sync

# Sync with all extras (dev, sse, viz)
uv sync --all-extras

# Add a new dependency
uv add requests

# Add a dev dependency
uv add --dev pytest-cov

# Remove a dependency
uv remove requests

# Upgrade all dependencies
uv sync --upgrade
```

### Running Python

```bash
# Run a Python script
uv run python scripts/start_server.py

# Run a module
uv run python -m bls_mcp.server

# Run an installed command
uv run bls-mcp

# Run pytest
uv run pytest tests/

# Run with arguments
uv run python scripts/test_mcp_client.py
```

### Development Commands

```bash
# Format code with black
uv run black src/ tests/

# Lint with ruff
uv run ruff check src/ tests/

# Auto-fix with ruff
uv run ruff check --fix src/ tests/

# Type check with mypy
uv run mypy src/

# Run a Python REPL with project installed
uv run python
```

## UV Convenience Scripts

We provide shell scripts for common tasks:

### Start Server

```bash
./scripts/uv_start_server.sh
```

Equivalent to:
```bash
uv run python scripts/start_server.py
```

### Test Client

```bash
./scripts/uv_test_client.sh
```

Equivalent to:
```bash
uv run python scripts/test_mcp_client.py
```

### Run Tests

```bash
./scripts/uv_test.sh

# Pass pytest arguments
./scripts/uv_test.sh -k test_get_series
./scripts/uv_test.sh --cov
```

## UV vs Traditional Virtualenv

### Traditional Way

```bash
python -m venv venv
source venv/bin/activate
pip install -e .
pip install pytest pytest-asyncio
python scripts/start_server.py
```

### UV Way

```bash
uv sync
uv run python scripts/start_server.py
```

Benefits:
- No need to manually activate virtualenv
- Automatic dependency resolution
- Lock file for reproducibility
- Much faster installation

## Project Structure with UV

```
bls_mcp/
├── .venv/              # Created by uv (gitignored)
├── uv.lock             # Dependency lock file (committed)
├── pyproject.toml      # Project config
├── scripts/
│   ├── uv_start_server.sh   # Start server with uv
│   ├── uv_test_client.sh    # Test client with uv
│   └── uv_test.sh           # Run tests with uv
└── ...
```

## Environment Management

### Virtual Environment Location

UV creates `.venv` in the project directory by default.

To use a different location:
```bash
UV_PROJECT_ENVIRONMENT=/path/to/venv uv sync
```

### Python Version

UV uses the Python version specified in `pyproject.toml`:
```toml
requires-python = ">=3.10"
```

To use a specific Python:
```bash
uv venv --python 3.11
uv sync
```

## Lock File

The `uv.lock` file ensures reproducible installs:

```bash
# Create/update lock file
uv lock

# Install from lock file (default)
uv sync

# Update lock file with new versions
uv lock --upgrade
```

**Important**: Commit `uv.lock` to version control!

## Integration with Claude Desktop

### Option 1: Using UV Script

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "bls-data": {
      "command": "/Users/YOUR_USERNAME/Downloads/projects/bls_food/bls_mcp/scripts/uv_start_server.sh"
    }
  }
}
```

### Option 2: Using UV Run

```json
{
  "mcpServers": {
    "bls-data": {
      "command": "uv",
      "args": [
        "run",
        "--project",
        "/Users/YOUR_USERNAME/Downloads/projects/bls_food/bls_mcp",
        "python",
        "scripts/start_server.py"
      ]
    }
  }
}
```

### Option 3: Using Absolute Path

```json
{
  "mcpServers": {
    "bls-data": {
      "command": "/Users/YOUR_USERNAME/.local/bin/uv",
      "args": [
        "run",
        "--project",
        "/Users/YOUR_USERNAME/Downloads/projects/bls_food/bls_mcp",
        "bls-mcp"
      ]
    }
  }
}
```

## Troubleshooting

### Issue: `uv: command not found`

**Solution**: Install uv or add it to PATH:
```bash
export PATH="$HOME/.local/bin:$PATH"
```

### Issue: Dependencies not syncing

**Solution**: Remove lock file and re-sync:
```bash
rm uv.lock
uv sync
```

### Issue: Wrong Python version

**Solution**: Specify Python version:
```bash
uv venv --python 3.11
uv sync
```

### Issue: Permission denied on scripts

**Solution**: Make scripts executable:
```bash
chmod +x scripts/uv_*.sh
```

## Performance Comparison

### Installation Time

```bash
# Traditional pip
time (python -m venv venv && source venv/bin/activate && pip install -e .)
# ~30-60 seconds

# UV
time uv sync
# ~2-5 seconds
```

### Cold Start (no cache)

```bash
# pip: ~45 seconds
# uv:  ~8 seconds
```

## Advanced UV Features

### Workspace Support

UV supports Python workspaces (monorepos). If you have multiple packages:

```toml
[tool.uv.workspace]
members = ["packages/*"]
```

### Custom Index

Use a custom PyPI index:

```bash
uv sync --index-url https://your-pypi.org/simple
```

### Offline Mode

Work without internet:

```bash
uv sync --offline
```

### Cache Management

```bash
# Show cache location
uv cache dir

# Clean cache
uv cache clean
```

## Best Practices

### 1. Commit uv.lock

Always commit `uv.lock` for reproducibility:
```bash
git add uv.lock
git commit -m "Update dependencies"
```

### 2. Use uv run

Instead of activating virtualenv:
```bash
# ✅ Good
uv run python script.py

# ❌ Avoid
source .venv/bin/activate
python script.py
```

### 3. Regular Updates

Keep dependencies updated:
```bash
# Weekly/monthly
uv lock --upgrade
uv sync
```

### 4. CI/CD

Use uv in CI/CD for faster builds:
```yaml
# .github/workflows/test.yml
- name: Install dependencies
  run: |
    curl -LsSf https://astral.sh/uv/install.sh | sh
    uv sync --all-extras

- name: Run tests
  run: uv run pytest
```

## Comparison with Other Tools

| Feature | uv | pip | poetry | pipenv |
|---------|----|----|--------|--------|
| Speed | ⚡⚡⚡ | ⚡ | ⚡⚡ | ⚡ |
| Lock files | ✅ | ❌ | ✅ | ✅ |
| Dependency resolution | ✅ | ⚠️ | ✅ | ✅ |
| Ease of use | ✅ | ✅ | ⚠️ | ⚠️ |
| Rust-based | ✅ | ❌ | ❌ | ❌ |

## Resources

- [UV Documentation](https://github.com/astral-sh/uv)
- [UV Installation Guide](https://github.com/astral-sh/uv#installation)
- [Project PLAN.md](../PLAN.md)
- [Quick Start Guide](QUICK_START.md)

## Summary

UV makes Python dependency management fast and reliable:

```bash
# Install
curl -LsSf https://astral.sh/uv/install.sh | sh

# Setup
cd bls_mcp
uv sync

# Run
./scripts/uv_start_server.sh
./scripts/uv_test_client.sh
./scripts/uv_test.sh

# That's it!
```

Enjoy the speed! 🚀
