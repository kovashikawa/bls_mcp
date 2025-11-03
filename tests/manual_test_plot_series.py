#!/usr/bin/env python3
"""Demo script showing the plot_series tool returning minimal data for client-side plotting."""

import asyncio
import json
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from bls_mcp.data.db_data_provider import DatabaseDataProvider
from bls_mcp.tools.plot_series import PlotSeriesTool


async def main():
    """Demonstrate the plot_series tool with minimal output."""
    print("=" * 70)
    print("plot_series Tool Demo - Minimal JSON for Client-Side Plotting")
    print("=" * 70)
    print()

    # Initialize tool with database provider
    try:
        data_provider = DatabaseDataProvider()
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        print("\nMake sure:")
        print("  1. PostgreSQL is running")
        print("  2. Database 'bls_data' exists")
        print("  3. Credentials in .env are correct")
        sys.exit(1)

    plot_tool = PlotSeriesTool(data_provider)

    # Call the tool with series_id parameter
    print("Calling plot_series tool for CUUR0000SA0 (CPI All Items)...")
    result = await plot_tool.execute({"series_id": "CUUR0000SA0"})

    # Also test with a different series and year range
    print("Also testing with year range (2020-2023)...")
    result_filtered = await plot_tool.execute({
        "series_id": "CUUR0000SA0",
        "start_year": 2020,
        "end_year": 2023
    })

    print("\n" + "=" * 70)
    print("MINIMAL JSON RESPONSE")
    print("=" * 70)
    print()
    print(f"Series ID: {result['series_id']}")
    print(f"Title: {result['title']}")
    print(f"Data points: {len(result['data'])}")
    print()

    print("=" * 70)
    print("DATA QUALITY METRICS")
    print("=" * 70)
    dq = result['data_quality']
    print(f"Has gaps:    {dq['has_gaps']}")
    print(f"Data points: {dq['data_points']}")
    print(f"Date range:  {dq['date_range']}")
    print(f"Frequency:   {dq['frequency']}")
    print(f"Notes:       {dq['notes']}")
    print()

    # Show first and last few data points
    print("=" * 70)
    print("SAMPLE DATA (First 5 and Last 5 Points)")
    print("=" * 70)
    print("\nFirst 5:")
    for point in result['data'][:5]:
        print(f"  {point['date']}: {point['value']}")

    print("\n...")
    print(f"\nLast 5:")
    for point in result['data'][-5:]:
        print(f"  {point['date']}: {point['value']}")
    print()

    # Show complete JSON (first 10 points)
    print("=" * 70)
    print("COMPLETE JSON (showing first 10 data points)")
    print("=" * 70)
    print()
    compact_result = {
        **result,
        'data': result['data'][:10] + [{"...": f"{len(result['data']) - 10} more points"}]
    }
    print(json.dumps(compact_result, indent=2))
    print()

    # Show statistics
    dates = [point['date'] for point in result['data']]
    values = [point['value'] for point in result['data']]
    print("=" * 70)
    print("DATA STATISTICS")
    print("=" * 70)
    print(f"Total points: {len(result['data'])}")
    print(f"Date range:   {dates[0]} to {dates[-1]}")
    print(f"Value range:  {min(values):.2f} to {max(values):.2f}")
    print(f"Average:      {sum(values)/len(values):.2f}")
    print()

    # Show how to use the data
    print("=" * 70)
    print("CLIENT-SIDE PLOTTING EXAMPLES")
    print("=" * 70)
    print()

    print("# Python with matplotlib:")
    print("-" * 70)
    print("import matplotlib.pyplot as plt")
    print("import json")
    print()
    print("data = json.loads(response)  # MCP tool response")
    print("dates = [point['date'] for point in data['data']]")
    print("values = [point['value'] for point in data['data']]")
    print()
    print("plt.figure(figsize=(12, 6))")
    print("plt.plot(dates, values, linewidth=2)")
    print("plt.title(data['title'])")
    print("plt.xlabel('Date')")
    print("plt.ylabel('Index Value')")
    print("plt.xticks(rotation=45)")
    print("plt.tight_layout()")
    print("plt.show()")
    print()

    print("# JavaScript with Chart.js:")
    print("-" * 70)
    print("const data = JSON.parse(response);  // MCP tool response")
    print("const chartData = {")
    print("  labels: data.data.map(d => d.date),")
    print("  datasets: [{")
    print("    label: data.title,")
    print("    data: data.data.map(d => d.value),")
    print("    borderColor: 'rgb(75, 192, 192)',")
    print("    tension: 0.1")
    print("  }]")
    print("};")
    print()

    print("=" * 70)
    print("FILTERED DATA (2020-2023)")
    print("=" * 70)
    print(f"Filtered to {len(result_filtered['data'])} points (vs {len(result['data'])} total)")
    dq_filtered = result_filtered['data_quality']
    print(f"Date range: {dq_filtered['date_range']}")
    print(f"Frequency:  {dq_filtered['frequency']}")
    print()

    print("=" * 70)
    print("✅ Demo Complete!")
    print("=" * 70)
    print()
    print("Benefits of this format:")
    print("  • Small payload size (date + value only)")
    print("  • LLMs won't truncate or omit data")
    print("  • Clean, readable format")
    print("  • Easy to parse and visualize")
    print("  • Works with any charting library")
    print("  • Supports optional year range filtering")
    print("  • Includes data quality metrics for context")
    print("  • Frequency and gap detection built-in")
    print()


if __name__ == "__main__":
    asyncio.run(main())
