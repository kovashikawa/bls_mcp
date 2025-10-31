#!/usr/bin/env python3
"""Manual test script to verify database connection and data provider.

Run this script directly to test the database connection:
    python tests/manual_test_database.py
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports (so `import bls_mcp` resolves)
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from bls_mcp.data.db_data_provider import DatabaseDataProvider


async def main():
    """Test database data provider."""
    print("=" * 70)
    print("DATABASE CONNECTION TEST")
    print("=" * 70)
    print()

    try:
        print("1. Initializing database provider...")
        provider = DatabaseDataProvider()
        print("   ✅ Database provider initialized\n")

        print("2. Testing list_series...")
        series_list = await provider.list_series(category="CPI", limit=5)
        print(f"   ✅ Found {len(series_list)} CPI series")
        if series_list:
            for series in series_list[:3]:
                title = series.get('series_title') or 'No title'
                print(f"      - {series['series_id']}: {title[:60]}...")
        else:
            print("      (No CPI series found - database may be empty)")
        print()

        print("3. Testing get_series_info...")
        info = await provider.get_series_info("CUUR0000SA0")
        print(f"   ✅ Retrieved info for {info['series_id']}")

        # Handle None values safely
        title = info.get('series_title') or '(No title in database)'
        print(f"      Title: {title}")
        print(f"      Data points: {info['data_point_count']}")
        print(f"      Area: {info.get('area', 'N/A')}")
        print(f"      Item: {info.get('item', 'N/A')}")
        print()

        print("4. Testing get_series...")
        series_data = await provider.get_series("CUUR0000SA0", start_year=2023)
        print(f"   ✅ Retrieved {series_data['count']} data points")

        # Safely handle metadata
        metadata = series_data.get('metadata', {})
        title = metadata.get('series_title') or '(No title)'
        area = metadata.get('area') or 'N/A'
        item = metadata.get('item') or 'N/A'

        print(f"      Series: {title}")
        print(f"      Area: {area}")
        print(f"      Item: {item}")

        if series_data['data']:
            first_point = series_data['data'][0]
            last_point = series_data['data'][-1]
            print(f"      First: {first_point['year']}-{first_point['period']} = {first_point['value']}")
            print(f"      Last:  {last_point['year']}-{last_point['period']} = {last_point['value']}")
        else:
            print("      (No data points returned)")
        print()

        print("=" * 70)
        print("✅ ALL TESTS PASSED!")
        print("=" * 70)
        print()
        print("Database provider is working correctly.")
        print("You can now start the MCP server with DATA_PROVIDER=database")
        print()

        # Print summary
        print("Summary:")
        print(f"  • Series in database: {len(series_list) if series_list else 'Unknown'}")
        print(f"  • CUUR0000SA0 data points: {info['data_point_count']}")
        print(f"  • 2023+ data points: {series_data['count']}")
        print()

    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print()
        print("Make sure:")
        print("  1. bls_data directory exists in parent directory")
        print("  2. Database dependencies installed: uv sync --extra database")
        print()
        sys.exit(1)

    except ConnectionError as e:
        print(f"❌ Connection Error: {e}")
        print()
        print("Make sure:")
        print("  1. PostgreSQL is running: brew services start postgresql@14")
        print("  2. Database 'bls_data' exists")
        print("  3. Credentials in .env are correct")
        print()
        print("Test connection with: psql -U postgres -d bls_data")
        print()
        sys.exit(1)

    except ValueError as e:
        print(f"❌ Data Error: {e}")
        print()
        print("The database connection works, but data may be missing.")
        print("Try running the data extraction scripts in bls_data/")
        print()
        print("Example:")
        print("  cd ../bls_data")
        print("  ./update_cpi_data.sh")
        print()
        sys.exit(1)

    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        print()
        import traceback
        traceback.print_exc()
        print()
        print("If you see 'NoneType' errors, this usually means:")
        print("  • Database has data but series_title column is NULL")
        print("  • This is normal and not a problem for the MCP server")
        print()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
