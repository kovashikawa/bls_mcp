# Visualization Tools - BLS MCP Server

Complete guide to using the visualization tools in the BLS MCP Server.

## Overview

The BLS MCP Server includes a simple, powerful visualization tool that creates static plots of BLS time series data. Charts are returned as base64-encoded PNG images that can be displayed directly in LLM interfaces like Claude Desktop.

## Features

- **Line Charts**: Perfect for visualizing trends over time
- **Bar Charts**: Great for comparing values across periods
- **Automatic Formatting**: Dates, labels, and axes are automatically formatted
- **Base64 Encoding**: Images are returned ready to display
- **Statistical Summary**: Min, max, and mean values included
- **Clean Design**: Professional-looking charts with minimal configuration

## Installation

Visualization tools require matplotlib and numpy. Install with:

```bash
# Using UV (recommended)
cd /Users/rafaelkovashikawa/Downloads/projects/bls_food/bls_mcp
uv sync --all-extras

# Or install just viz extras
uv sync --extra viz
```

## The `plot_series` Tool

### Basic Usage

**Minimal Example:**
```json
{
  "series_id": "CUUR0000SA0"
}
```

**With Date Range:**
```json
{
  "series_id": "CUUR0000SA0",
  "start_year": 2023,
  "end_year": 2024
}
```

**Bar Chart:**
```json
{
  "series_id": "CUUR0000SA0",
  "chart_type": "bar"
}
```

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `series_id` | string | Yes | - | BLS series ID (e.g., "CUUR0000SA0") |
| `start_year` | integer | No | null | Start year for data range |
| `end_year` | integer | No | null | End year for data range |
| `chart_type` | string | No | "line" | Chart type: "line" or "bar" |

### Return Format

The tool returns a JSON object with the following structure:

```json
{
  "status": "success",
  "series_id": "CUUR0000SA0",
  "title": "All items in U.S. city average, all urban consumers, seasonally adjusted",
  "chart_type": "line",
  "data_points": 21,
  "date_range": {
    "start": "2023-01",
    "end": "2024-09"
  },
  "value_range": {
    "min": 299.17,
    "max": 314.54,
    "mean": 307.87
  },
  "image": {
    "format": "png",
    "encoding": "base64",
    "data": "iVBORw0KGgoAAAANSUhEUgAAA..."
  },
  "message": "Created line chart for ... with 21 data points"
}
```

### Image Data

The `image.data` field contains a base64-encoded PNG image. To use it:

**In Python:**
```python
import base64
from pathlib import Path

# Decode and save
image_data = base64.b64decode(result["image"]["data"])
Path("chart.png").write_bytes(image_data)
```

**In HTML:**
```html
<img src="data:image/png;base64,{image_data}" alt="BLS Chart">
```

**In Markdown (if supported):**
```markdown
![BLS Chart](data:image/png;base64,{image_data})
```

## Examples

### Example 1: Basic Line Chart

Visualize CPI trends for "All Items":

```python
{
  "series_id": "CUUR0000SA0",
  "start_year": 2023,
  "end_year": 2024,
  "chart_type": "line"
}
```

**Result:** A line chart showing monthly CPI values from 2023-2024.

### Example 2: Food CPI Bar Chart

Compare food prices across months:

```python
{
  "series_id": "CUUR0000SAF",
  "start_year": 2024,
  "chart_type": "bar"
}
```

**Result:** A bar chart showing food CPI for each month in 2024.

### Example 3: Long-term Trends

View 5 years of data:

```python
{
  "series_id": "CUUR0000SA0",
  "start_year": 2020,
  "end_year": 2024
}
```

**Result:** A line chart showing the full 5-year trend.

### Example 4: Comparing Chart Types

Same data, different visualizations:

**Line Chart** - Better for trends:
```python
{"series_id": "CUUR0000SA0", "chart_type": "line"}
```

**Bar Chart** - Better for comparisons:
```python
{"series_id": "CUUR0000SA0", "chart_type": "bar"}
```

## Using with MCP Clients

### Claude Desktop (Local)

Once the BLS MCP server is connected to Claude Desktop, you can ask Claude to create visualizations:

### Example Prompts

**Simple visualization:**
```
Can you create a line chart of the CPI data for series CUUR0000SA0 from 2023 to 2024?
```

**Comparing data:**
```
Show me a bar chart comparing food prices (CUUR0000SAF) over the last year.
```

**With analysis:**
```
Plot the housing CPI data and tell me if you see any notable trends.
```

Claude will:
1. Call the `plot_series` tool with appropriate parameters
2. Display the generated chart image
3. Provide analysis based on the data and visualization

### Remote Access via ngrok (SSE Transport)

The visualization tool is also available via the SSE transport for remote access:

**Start the ngrok server:**
```bash
cd /Users/rafaelkovashikawa/Downloads/projects/bls_food/bls_mcp
uv run python scripts/start_ngrok.py
```

**You'll see:**
```
✅ ngrok tunnel created successfully!
🔗 Public URL: https://xxxx-xxx-xxx-xxx.ngrok-free.app
📡 Local server: http://localhost:3000
```

**Test the endpoints:**
```bash
# Check available tools
curl https://your-ngrok-url.ngrok-free.app/

# List tools via MCP
curl -X POST https://your-ngrok-url.ngrok-free.app/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

The `plot_series` tool will be included in the response and can be called from any MCP-compatible client that supports HTTP/SSE transport.

## Testing the Visualization Tool

### Command Line Test

Run the test script to generate sample charts:

```bash
cd /Users/rafaelkovashikawa/Downloads/projects/bls_food/bls_mcp
uv run python scripts/test_visualization.py
```

This will create several test charts in the project directory:
- `test_line_chart.png` - Example line chart
- `test_bar_chart.png` - Example bar chart
- `test_series_*.png` - Charts for different series

### Python Test

```python
import asyncio
import base64
from pathlib import Path
from bls_mcp.data.mock_data import MockDataProvider
from bls_mcp.tools.plot_series import PlotSeriesTool

async def create_chart():
    provider = MockDataProvider()
    tool = PlotSeriesTool(provider)

    result = await tool.execute({
        "series_id": "CUUR0000SA0",
        "start_year": 2023,
        "chart_type": "line"
    })

    if result["status"] == "success":
        # Save the image
        image_data = base64.b64decode(result["image"]["data"])
        Path("my_chart.png").write_bytes(image_data)
        print(f"Chart created: {result['title']}")
        print(f"Data points: {result['data_points']}")
        print(f"Saved to: my_chart.png")

asyncio.run(create_chart())
```

### Unit Tests

Run the visualization unit tests:

```bash
# Run only visualization tests
uv run pytest tests/test_plot_series.py -v

# Run all tests
uv run pytest tests/ -v
```

## Chart Customization

Currently, the charts have a fixed, clean design optimized for readability. Future enhancements may include:

- Color themes
- Custom labels and titles
- Multiple series on one chart
- Different chart types (scatter, area, etc.)
- Interactive charts

## Troubleshooting

### Issue: "matplotlib is required"

**Error:**
```
ImportError: matplotlib is required for visualization tools
```

**Solution:**
```bash
uv sync --all-extras
```

### Issue: Tool not appearing in Claude Desktop

**Solution:**
1. Make sure viz extras are installed
2. Restart the MCP server
3. Restart Claude Desktop
4. Check logs: `tail -f ~/Library/Logs/Claude/mcp-server-bls-mcp.log`

### Issue: Image not displaying

The tool returns base64-encoded images. If the image doesn't display:

1. **Check the status field**: Should be "success"
2. **Verify image data exists**: `result["image"]["data"]` should be a long string
3. **Try saving to file**: Decode and save as PNG to verify image is valid
4. **Check LLM support**: Some interfaces may not support base64 images

### Issue: "No data points available"

**Cause:** No data available for the specified date range.

**Solution:**
- Check series_id is valid
- Verify date range has data
- Try without date range to see all available data

## Performance Notes

- Chart generation is fast (~0.5-1 second per chart)
- Images are typically 20-40KB in size
- Base64 encoding adds ~33% to size
- Multiple charts can be generated in parallel

## API Integration

The visualization tool integrates seamlessly with the other BLS MCP tools:

### Workflow Example

```python
# 1. List available series
series_list = await list_series_tool.execute({"category": "cpi"})

# 2. Get detailed info
info = await get_series_info_tool.execute({"series_id": "CUUR0000SA0"})

# 3. Visualize the data
chart = await plot_series_tool.execute({
    "series_id": "CUUR0000SA0",
    "start_year": 2023
})

# 4. Analyze the results
print(f"Series: {info['title']}")
print(f"Value range: {chart['value_range']['min']} - {chart['value_range']['max']}")
```

## Future Enhancements

Planned improvements for visualization tools:

### Phase 2 (Current)
- [x] Basic line charts
- [x] Basic bar charts
- [x] Base64-encoded images
- [ ] Multiple series comparison
- [ ] Trend analysis

### Phase 3 (Future)
- [ ] Interactive charts
- [ ] Custom styling
- [ ] Export formats (SVG, PDF)
- [ ] Chart templates
- [ ] Statistical overlays (moving averages, etc.)

## Related Documentation

- [README.md](../README.md) - Project overview
- [QUICK_START.md](QUICK_START.md) - Getting started guide
- [CLAUDE_DESKTOP_SETUP.md](CLAUDE_DESKTOP_SETUP.md) - Claude Desktop integration
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues

## Support

For issues or questions about visualization tools:

1. Check this documentation
2. Run the test script: `scripts/test_visualization.py`
3. Check unit tests: `tests/test_plot_series.py`
4. Review generated charts in project root

---

**Status**: Production Ready
**Last Updated**: October 17, 2025
**Phase**: 2 - Enhanced Tools
