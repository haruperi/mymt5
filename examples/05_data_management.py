from mylogger import logger
"""
MT5Data Usage Examples

This example demonstrates comprehensive usage of the MT5Data class for:
- Retrieving OHLCV bar data
- Retrieving tick data
- Real-time data streaming
- Data processing and cleaning
- Caching mechanisms
- Exporting data to various formats
- Statistical analysis
"""

from mymt5.client import MT5Client
from mymt5.data import MT5Data
from mymt5.enums import TimeFrame
from datetime import datetime, timedelta
import pandas as pd
import configparser


def _get_demo_credentials():
    config = configparser.ConfigParser()
    config.read('config.ini')
    section = 'DEMO'
    return (
        int(config[section]['login']),
        config[section]['password'],
        config[section]['server'],
        config[section]['path']
    )


def example1_basic_bars():
    """Example 1: Basic OHLCV bar data retrieval."""
    print("\n" + "="*60)
    print("Example 1: Retrieving OHLCV Bar Data")
    print("="*60)

    # Initialize client and data
    client = MT5Client()
    login, password, server, path = _get_demo_credentials()
    client.initialize(login=login, password=password, server=server, path=path)

    data = MT5Data(client=client)

    # Get last 100 H1 bars
    bars = data.get_bars("EURUSD", TimeFrame.H1, count=100)
    if bars is not None:
        print(f"\nRetrieved {len(bars)} bars")
        print(f"\nFirst 5 bars:")
        print(bars.head())
        print(f"\nLast 5 bars:")
        print(bars.tail())

    client.disconnect()


def example2_date_range():
    """Example 2: Retrieving data for a specific date range."""
    print("\n" + "="*60)
    print("Example 2: Date Range Data Retrieval")
    print("="*60)

    client = MT5Client()
    login, password, server, path = _get_demo_credentials()
    client.initialize(login=login, password=password, server=server, path=path)

    data = MT5Data(client=client)

    # Get data for specific date range
    start = datetime(2024, 1, 1)
    end = datetime(2024, 1, 31)

    bars = data.get_bars("EURUSD", TimeFrame.D1, start=start, end=end)
    if bars is not None:
        print(f"\nRetrieved {len(bars)} daily bars from {start.date()} to {end.date()}")
        print(f"\nSummary statistics:")
        # Columns are capitalized after recent changes
        print(bars[['Open', 'High', 'Low', 'Close']].describe())

    client.disconnect()


def example3_tick_data():
    """Example 3: Retrieving tick data."""
    print("\n" + "="*60)
    print("Example 3: Tick Data Retrieval")
    print("="*60)

    client = MT5Client()
    login, password, server, path = _get_demo_credentials()
    client.initialize(login=login, password=password, server=server, path=path)

    data = MT5Data(client=client)

    # Get last 1000 ticks
    ticks = data.get_ticks("EURUSD", count=1000)
    if ticks is not None:
        print(f"\nRetrieved {len(ticks)} ticks")
        print(f"\nFirst 5 ticks:")
        print(ticks.head())

        # Calculate bid-ask spread (columns are capitalized)
        ticks['Spread'] = ticks['Ask'] - ticks['Bid']
        print(f"\nAverage spread: {ticks['Spread'].mean():.5f}")
        print(f"Min spread: {ticks['Spread'].min():.5f}")
        print(f"Max spread: {ticks['Spread'].max():.5f}")

    client.disconnect()


def example4_streaming_ticks():
    """Example 4: Real-time tick streaming."""
    print("\n" + "="*60)
    print("Example 4: Real-Time Tick Streaming")
    print("="*60)

    client = MT5Client()
    login, password, server, path = _get_demo_credentials()
    client.initialize(login=login, password=password, server=server, path=path)

    data = MT5Data(client=client)

    # Define callback for new ticks
    tick_count = 0
    def on_tick(tick_data):
        nonlocal tick_count
        tick_count += 1
        print(f"Tick #{tick_count}: {tick_data['time']} - Bid: {tick_data['bid']:.5f}, Ask: {tick_data['ask']:.5f}")

    # Start streaming
    print("\nStreaming ticks for 10 seconds...")
    data.stream("EURUSD", "ticks", callback=on_tick)

    # Let it run for 10 seconds
    import time
    time.sleep(10)

    # Stop streaming
    data.stop_stream("EURUSD", "ticks")
    print(f"\nStreaming stopped. Total ticks received: {tick_count}")

    client.disconnect()


def example5_streaming_bars():
    """Example 5: Real-time bar streaming."""
    print("\n" + "="*60)
    print("Example 5: Real-Time Bar Streaming")
    print("="*60)

    client = MT5Client()
    login, password, server, path = _get_demo_credentials()
    client.initialize(login=login, password=password, server=server, path=path)

    data = MT5Data(client=client)

    # Define callback for new bars
    def on_bar(bar_data):
        print(f"New bar: {bar_data['time']} - O: {bar_data['open']:.5f}, H: {bar_data['high']:.5f}, "
              f"L: {bar_data['low']:.5f}, C: {bar_data['close']:.5f}")

    # Start streaming M1 bars
    print("\nStreaming M1 bars for 5 minutes...")
    data.stream("EURUSD", "bars", callback=on_bar, timeframe=TimeFrame.M1, interval=60)

    # Let it run for 5 minutes
    import time
    time.sleep(300)

    # Stop streaming
    data.stop_stream("EURUSD", "bars")
    print("\nStreaming stopped.")

    client.disconnect()


def example6_data_processing():
    """Example 6: Data processing and cleaning."""
    print("\n" + "="*60)
    print("Example 6: Data Processing")
    print("="*60)

    client = MT5Client()
    login, password, server, path = _get_demo_credentials()
    client.initialize(login=login, password=password, server=server, path=path)

    data = MT5Data(client=client)

    # Get data
    bars = data.get_bars("EURUSD", TimeFrame.H1, count=500)
    if bars is not None:
        print(f"\nOriginal data: {len(bars)} bars")

        # Clean data
        clean_bars = data.process(bars, 'clean')
        print(f"After cleaning: {len(clean_bars)} bars")

        # Normalize data
        normalized = data.process(clean_bars, 'normalize', method='minmax')
        print("\nNormalized close prices (first 5):")
        print(normalized[['Close', 'Close_normalized']].head())

        # Resample to 4H
        resampled = data.process(clean_bars, 'resample', timeframe='4h')
        print(f"\nResampled to 4H: {len(resampled)} bars")

        # Detect gaps
        gaps = data.process(clean_bars, 'detect_gaps', timeframe_minutes=60)
        if len(gaps) > 0:
            print(f"\nDetected {len(gaps)} gaps in data")
            print(gaps.head())
        else:
            print("\nNo gaps detected")

    client.disconnect()


def example7_caching():
    """Example 7: Using data caching."""
    print("\n" + "="*60)
    print("Example 7: Data Caching")
    print("="*60)

    client = MT5Client()
    login, password, server, path = _get_demo_credentials()
    client.initialize(login=login, password=password, server=server, path=path)

    data = MT5Data(client=client)

    # Retrieve and cache data
    print("\nRetrieving data (first time - from MT5)...")
    import time
    start_time = time.time()
    bars = data.get_bars("EURUSD", TimeFrame.H1, count=1000)
    first_time = time.time() - start_time
    print(f"Time taken: {first_time:.4f} seconds")

    # Cache the data
    data.cache("eurusd_h1_1000", bars, ttl=300)  # Cache for 5 minutes
    print("\nData cached")

    # Retrieve from cache
    print("\nRetrieving data (from cache)...")
    start_time = time.time()
    cached_bars = data.get_cached("eurusd_h1_1000")
    cache_time = time.time() - start_time
    print(f"Time taken: {cache_time:.4f} seconds")
    print(f"Speed improvement: {first_time/cache_time:.2f}x faster")

    # Clear specific cache
    data.clear_cache("eurusd_h1_1000")
    print("\nCache cleared")

    # Try to retrieve again (should return None)
    result = data.get_cached("eurusd_h1_1000")
    print(f"Cache after clearing: {result}")

    client.disconnect()


def example8_export_data():
    """Example 8: Exporting data to various formats."""
    print("\n" + "="*60)
    print("Example 8: Exporting Data")
    print("="*60)

    client = MT5Client()
    login, password, server, path = _get_demo_credentials()
    client.initialize(login=login, password=password, server=server, path=path)

    data = MT5Data(client=client)

    # Get data
    bars = data.get_bars("EURUSD", TimeFrame.H1, count=100)
    if bars is not None:
        # Export to CSV
        csv_success = data.export(bars, "data/eurusd_h1.csv", format='csv')
        print(f"\nCSV export: {'Success' if csv_success else 'Failed'}")

        # Export to JSON
        json_success = data.export(bars, "data/eurusd_h1.json", format='json')
        print(f"JSON export: {'Success' if json_success else 'Failed'}")

        # Export to Pickle
        pickle_success = data.export(bars, "data/eurusd_h1.pkl", format='pickle')
        print(f"Pickle export: {'Success' if pickle_success else 'Failed'}")

    client.disconnect()


def example9_statistics():
    """Example 9: Statistical analysis."""
    print("\n" + "="*60)
    print("Example 9: Statistical Analysis")
    print("="*60)

    client = MT5Client()
    login, password, server, path = _get_demo_credentials()
    client.initialize(login=login, password=password, server=server, path=path)

    data = MT5Data(client=client)

    # Get data for multiple timeframes
    symbols = ["EURUSD", "GBPUSD", "USDJPY"]

    for symbol in symbols:
        print(f"\n{'='*40}")
        print(f"Analysis for {symbol}")
        print(f"{'='*40}")

        bars = data.get_bars(symbol, TimeFrame.H1, count=500)
        if bars is not None:
            # Get summary
            summary = data.get_summary(bars)
            print(f"\nData summary:")
            print(f"  Rows: {summary['rows']}")
            print(f"  Date range: {summary['date_range']['start']} to {summary['date_range']['end']}")
            print(f"  Duration: {summary['date_range']['duration']}")

            # Calculate statistics
            stats = data.calculate_stats(bars)
            print(f"\nStatistical measures:")
            print(f"  Total return: {stats['total_return']:.2f}%")
            print(f"  Volatility: {stats['volatility']:.2f}%")
            print(f"  Sharpe ratio: {stats['sharpe_ratio']:.2f}")
            print(f"  Max drawdown: {stats['max_drawdown']:.2f}%")
            print(f"  Price range: {stats['price_range']:.5f} ({stats['price_range_pct']:.2f}%)")

    client.disconnect()


def example10_complete_workflow():
    """Example 10: Complete data management workflow."""
    print("\n" + "="*60)
    print("Example 10: Complete Data Management Workflow")
    print("="*60)

    client = MT5Client()
    login, password, server, path = _get_demo_credentials()
    client.initialize(login=login, password=password, server=server, path=path)

    data = MT5Data(client=client)

    # 1. Retrieve data
    print("\n1. Retrieving data...")
    bars = data.get_bars("EURUSD", TimeFrame.H1, count=1000)

    if bars is not None:
        # 2. Process data
        print("\n2. Processing data...")
        clean_bars = data.process(bars, 'clean')
        filled_bars = data.process(clean_bars, 'fill_missing', method='ffill')

        # 3. Analyze data
        print("\n3. Analyzing data...")
        summary = data.get_summary(filled_bars)
        stats = data.calculate_stats(filled_bars)

        print(f"\nData quality:")
        print(f"  Original rows: {len(bars)}")
        print(f"  After processing: {len(filled_bars)}")
        print(f"  Data loss: {(1 - len(filled_bars)/len(bars))*100:.2f}%")

        print(f"\nPerformance:")
        print(f"  Return: {stats['total_return']:.2f}%")
        print(f"  Volatility: {stats['volatility']:.2f}%")
        print(f"  Sharpe: {stats['sharpe_ratio']:.2f}")

        # 4. Cache for later use
        print("\n4. Caching data...")
        data.cache("eurusd_processed", filled_bars, ttl=3600)

        # 5. Export for external analysis
        print("\n5. Exporting data...")
        data.export(filled_bars, "data/eurusd_processed.csv", format='csv')
        data.export(filled_bars, "data/eurusd_processed.json", format='json')

        print("\n✓ Workflow completed successfully!")

    client.disconnect()


def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("MT5Data Usage Examples")
    print("="*60)

    examples = [
        ("Basic Bar Retrieval", example1_basic_bars),
        ("Date Range Retrieval", example2_date_range),
        ("Tick Data", example3_tick_data),
        ("Tick Streaming", example4_streaming_ticks),
        ("Bar Streaming", example5_streaming_bars),
        ("Data Processing", example6_data_processing),
        ("Caching", example7_caching),
        ("Data Export", example8_export_data),
        ("Statistics", example9_statistics),
        ("Complete Workflow", example10_complete_workflow),
    ]

    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")

    print("\nNote: Some examples (streaming) may take several minutes to complete.")

    # Run a few quick examples by default
    try:
        example1_basic_bars()
        example2_date_range()
        example3_tick_data()
        example6_data_processing()
        example7_caching()
        example8_export_data()
        example9_statistics()
        example10_complete_workflow()

        print("\n" + "="*60)
        print("All examples completed successfully!")
        print("="*60)

    except Exception as e:
        logger.error(f"Error running examples: {e}")
        print(f"\nError: {e}")
        print("Make sure MT5 is running and you have valid credentials configured.")


if __name__ == "__main__":
    main()
