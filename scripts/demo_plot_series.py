#!/usr/bin/env python3
"""Demo script showing the new plot_series tool returning data for client-side plotting."""

import asyncio
import json
from bls_mcp.data.mock_data import MockDataProvider
from bls_mcp.tools.plot_series import PlotSeriesTool


async def main():
    """Demonstrate the plot_series tool."""
    print("=" * 70)
    print("plot_series Tool Demo - Client-Side Data Formatting")
    print("=" * 70)
    print()

    # Initialize tool
    data_provider = MockDataProvider()
    plot_tool = PlotSeriesTool(data_provider)

    # Call the tool
    print("Calling plot_series tool (no parameters needed)...")
    result = await plot_tool.execute({})

    print("\n" + "=" * 70)
    print("RESPONSE STRUCTURE")
    print("=" * 70)
    print()
    print(f"Status: {result['status']}")
    print(f"Series ID: {result['series_id']}")
    print(f"Series Title: {result['series_title']}")
    print()

    # Show statistics
    print("=" * 70)
    print("STATISTICS")
    print("=" * 70)
    stats = result['statistics']
    print(f"Data Points: {stats['count']}")
    print(f"Min Value:   {stats['min']}")
    print(f"Max Value:   {stats['max']}")
    print(f"Average:     {stats['average']}")
    print()

    # Show date range
    print("=" * 70)
    print("DATE RANGE")
    print("=" * 70)
    date_range = result['date_range']
    print(f"Start: {date_range['start']}")
    print(f"End:   {date_range['end']}")
    print()

    # Show first few data points
    print("=" * 70)
    print("SAMPLE DATA (First 5 Points)")
    print("=" * 70)
    for point in result['data'][:5]:
        print(f"{point['date']}: {point['value']:.3f}")
    print("...")
    print()

    # Show plot instructions
    print("=" * 70)
    print("PLOT INSTRUCTIONS")
    print("=" * 70)
    instructions = result['plot_instructions']
    print(f"Chart Type: {instructions['chart_type']}")
    print(f"X-Axis:     {instructions['x_axis']} ({instructions['x_label']})")
    print(f"Y-Axis:     {instructions['y_axis']} ({instructions['y_label']})")
    print(f"Title:      {instructions['title']}")
    print()

    # Show how to use the data
    print("=" * 70)
    print("CLIENT-SIDE PLOTTING EXAMPLE")
    print("=" * 70)
    print()
    print("# Python with matplotlib:")
    print("import matplotlib.pyplot as plt")
    print()
    print("dates = [point['date'] for point in data['data']]")
    print("values = [point['value'] for point in data['data']]")
    print()
    print("plt.figure(figsize=(12, 6))")
    print("plt.plot(dates, values)")
    print("plt.title(data['series_title'])")
    print("plt.xlabel('Date')")
    print("plt.ylabel('Index Value')")
    print("plt.xticks(rotation=45)")
    print("plt.tight_layout()")
    print("plt.show()")
    print()

    print("=" * 70)
    print("JSON OUTPUT (for ChatGPT/Claude)")
    print("=" * 70)
    print()
    # Show compact JSON
    compact_result = {
        **result,
        'data': result['data'][:3] + [{"...": f"{len(result['data']) - 3} more points"}]
    }
    print(json.dumps(compact_result, indent=2))
    print()

    print("=" * 70)
    print("✅ Demo Complete!")
    print("=" * 70)
    print()
    print("This data can be used by:")
    print("  • ChatGPT - Built-in charting capabilities")
    print("  • Claude - Data analysis and trend description")
    print("  • Custom clients - matplotlib, Chart.js, D3.js, Plotly, etc.")
    print()


if __name__ == "__main__":
    asyncio.run(main())
