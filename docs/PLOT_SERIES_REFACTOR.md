# plot_series Tool Refactor - Client-Side Plotting Approach

**Date**: October 30, 2025
**Status**: Complete ✅
**Tests**: 26/26 passing

## Summary

Refactored the `plot_series` tool from server-side image generation (base64-encoded PNGs) to client-side data formatting. This approach is more stable and works reliably across different LLM clients (ChatGPT, Claude, etc.).

## Problem

The original implementation generated charts on the server using matplotlib and returned base64-encoded PNG images. Testing showed this approach was unstable:
- ChatGPT and Claude had issues loading the base64 images
- Large image data bloated responses
- Required optional matplotlib dependency
- Less flexible for clients

## Solution

Changed `plot_series` to return structured JSON data suitable for client-side plotting:
- Returns time series data as arrays of objects
- Includes statistics (min, max, average)
- Provides plot instructions for rendering
- No image generation on server
- No matplotlib dependency required

## Changes Made

### 1. Modified `plot_series.py`
- **Removed**: matplotlib imports, image generation code, base64 encoding
- **Added**: Data formatting logic, statistics calculation, plot instructions
- **Result**: Simpler, faster, no external dependencies

**Key changes:**
- Returns array of `{date, value, year, month, period}` objects
- Calculates statistics (count, min, max, average)
- Provides date range (start, end)
- Includes plot instructions for client rendering

### 2. Updated `server.py`
- Removed special handling for `plot_series` image responses
- Removed `ImageContent` import
- All tools now return uniform JSON text responses
- Simplified response handling logic

### 3. Rewrote Tests (`test_plot_series.py`)
- Replaced 9 image-focused tests with 9 data-focused tests
- Tests verify data structure, statistics, sorting, format
- All tests passing (9/9)

### 4. Updated Documentation
- [README.md](../README.md): Updated tool description with example response
- [CLAUDE.md](../CLAUDE.md): Updated critical implementation details
- Removed references to matplotlib/viz extras requirement

## New Response Format

```json
{
  "status": "success",
  "series_id": "CUUR0000SA0",
  "series_title": "Consumer Price Index for All Urban Consumers: All Items",
  "data": [
    {
      "date": "2020-01",
      "value": 257.971,
      "year": "2020",
      "month": "01",
      "period": "M01"
    },
    ...
  ],
  "statistics": {
    "count": 60,
    "min": 257.971,
    "max": 314.540,
    "average": 285.234
  },
  "date_range": {
    "start": "2020-01",
    "end": "2024-12"
  },
  "plot_instructions": {
    "chart_type": "line",
    "x_axis": "date",
    "y_axis": "value",
    "title": "Consumer Price Index for All Urban Consumers: All Items",
    "x_label": "Date",
    "y_label": "Index Value"
  }
}
```

## Benefits

1. **Stability**: Works reliably across all LLM clients
2. **Flexibility**: Clients can render charts in their preferred format
3. **Simplicity**: No server-side image generation complexity
4. **Performance**: Faster response times, smaller payloads
5. **No Dependencies**: Removed matplotlib requirement
6. **Client Control**: Clients can customize visualization

## Usage with LLM Clients

### ChatGPT
ChatGPT can use the data to generate charts using its built-in charting capabilities:
```
User: "Plot the CPI data"
ChatGPT: [Calls plot_series tool, receives data, renders chart using internal tools]
```

### Claude Desktop
Claude can analyze the data and describe trends:
```
User: "Show me CPI trends"
Claude: [Calls plot_series tool, analyzes data, describes trends with statistics]
```

### Custom Clients
Any client can use the data with libraries like:
- matplotlib (Python)
- Chart.js (JavaScript)
- D3.js (JavaScript)
- Plotly (Python/JavaScript)

## Migration Notes

### Breaking Changes
- Tool no longer returns `image` field with base64 data
- Now returns `data` array with plot instructions
- No parameters required (hardcoded to CUUR0000SA0)

### Backwards Compatibility
This is a breaking change. Clients expecting image data will need to:
1. Update to use the new `data` field
2. Implement their own rendering logic
3. Remove any base64 decoding code

## Test Results

```bash
$ uv run pytest tests/ -v
============================= test session starts ==============================
collected 26 items

tests/test_mock_data.py .........                                        [ 34%]
tests/test_plot_series.py .........                                      [ 69%]
tests/test_tools.py ........                                             [100%]

============================== 26 passed in 0.16s ===============================
```

## Files Modified

1. `src/bls_mcp/tools/plot_series.py` - Complete rewrite
2. `src/bls_mcp/server.py` - Simplified response handling
3. `tests/test_plot_series.py` - Rewrote all 9 tests
4. `README.md` - Updated tool documentation
5. `CLAUDE.md` - Updated implementation notes

## Files Created

1. `docs/PLOT_SERIES_REFACTOR.md` - This document

## Next Steps

This refactor sets the foundation for:
1. Adding more series support (beyond CUUR0000SA0)
2. Supporting multiple series comparison
3. Adding parameters for date range filtering
4. Creating additional data formatting tools

## Conclusion

The refactor successfully transitions from server-side image generation to client-side data formatting. This approach is more stable, flexible, and performant. All tests pass and the tool works correctly with MCP clients.
