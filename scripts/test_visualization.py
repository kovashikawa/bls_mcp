#!/usr/bin/env python3
"""Test script for visualization tool - generates sample plots."""

import asyncio
import base64
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from bls_mcp.data.mock_data import MockDataProvider
from bls_mcp.tools.plot_series import PlotSeriesTool


async def test_line_chart():
    """Test creating a line chart and save it."""
    print("📊 Testing line chart visualization...")

    provider = MockDataProvider()
    tool = PlotSeriesTool(provider)

    result = await tool.execute({
        "series_id": "CUUR0000SA0",
        "start_year": 2023,
        "end_year": 2024,
        "chart_type": "line"
    })

    if result["status"] == "success":
        print(f"✅ Line chart created successfully!")
        print(f"   Series: {result['title']}")
        print(f"   Data points: {result['data_points']}")
        print(f"   Date range: {result['date_range']['start']} to {result['date_range']['end']}")
        print(f"   Value range: {result['value_range']['min']:.2f} to {result['value_range']['max']:.2f}")
        print(f"   Mean value: {result['value_range']['mean']:.2f}")

        # Save image
        image_data = base64.b64decode(result["image"]["data"])
        output_file = Path(__file__).parent.parent / "test_line_chart.png"
        output_file.write_bytes(image_data)
        print(f"   📁 Saved to: {output_file}")
    else:
        print(f"❌ Error: {result.get('error')}")

    return result


async def test_bar_chart():
    """Test creating a bar chart and save it."""
    print("\n📊 Testing bar chart visualization...")

    provider = MockDataProvider()
    tool = PlotSeriesTool(provider)

    result = await tool.execute({
        "series_id": "CUUR0000SAF",  # Food series
        "start_year": 2023,
        "end_year": 2024,
        "chart_type": "bar"
    })

    if result["status"] == "success":
        print(f"✅ Bar chart created successfully!")
        print(f"   Series: {result['title']}")
        print(f"   Data points: {result['data_points']}")
        print(f"   Date range: {result['date_range']['start']} to {result['date_range']['end']}")
        print(f"   Value range: {result['value_range']['min']:.2f} to {result['value_range']['max']:.2f}")

        # Save image
        image_data = base64.b64decode(result["image"]["data"])
        output_file = Path(__file__).parent.parent / "test_bar_chart.png"
        output_file.write_bytes(image_data)
        print(f"   📁 Saved to: {output_file}")
    else:
        print(f"❌ Error: {result.get('error')}")

    return result


async def test_multiple_series():
    """Test visualizing multiple different series."""
    print("\n📊 Testing multiple series...")

    provider = MockDataProvider()
    tool = PlotSeriesTool(provider)

    # Get list of all series
    series_list = await provider.list_series()
    print(f"   Found {len(series_list)} series")

    # Create plots for first 3 series
    for i, series in enumerate(series_list[:3]):
        series_id = series["series_id"]
        print(f"\n   [{i+1}/3] Creating plot for {series_id}...")

        result = await tool.execute({
            "series_id": series_id,
            "start_year": 2023,
            "chart_type": "line"
        })

        if result["status"] == "success":
            print(f"   ✅ {result['title'][:50]}...")

            # Save image
            image_data = base64.b64decode(result["image"]["data"])
            output_file = Path(__file__).parent.parent / f"test_series_{series_id}.png"
            output_file.write_bytes(image_data)
            print(f"      📁 {output_file.name}")
        else:
            print(f"   ❌ Error: {result.get('error')}")


async def main():
    """Run all visualization tests."""
    print("=" * 60)
    print("BLS MCP Visualization Tool Test")
    print("=" * 60)

    try:
        # Test line chart
        await test_line_chart()

        # Test bar chart
        await test_bar_chart()

        # Test multiple series
        await test_multiple_series()

        print("\n" + "=" * 60)
        print("✅ All visualization tests completed!")
        print("=" * 60)
        print("\n📁 Generated files:")
        output_dir = Path(__file__).parent.parent
        for png_file in output_dir.glob("test_*.png"):
            print(f"   - {png_file.name}")

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
