"""
MT5Symbol Usage Examples

This module demonstrates various ways to use the MT5Symbol class
for managing symbols, retrieving symbol information, and validating trading parameters.
"""

import sys
import os
from pathlib import Path

# Add project root to Python path to allow imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mylogger import logger
from mymt5.client import MT5Client
from mymt5.symbol import MT5Symbol
import configparser


logger.info("Loading symbol management examples")


def get_credentials_from_config(config_file='config.ini', section='MT5'):
    """
    Load MT5 credentials from config file.

    Args:
        config_file: Path to config file (default: 'config.ini')
        section: Section name in config file (default: 'MT5')

    Returns:
        dict: Dictionary with 'login', 'password', 'server', and optionally 'path'
        None: If config file or section not found
    """
    config = configparser.ConfigParser()

    # Resolve config file path - try current dir first, then project root
    config_path = Path(config_file)
    if not config_path.exists():
        # Try in project root (parent of examples directory)
        project_root = Path(__file__).parent.parent
        config_path = project_root / config_file

    # Check if config file exists
    if not config_path.exists():
        logger.warning(f"Config file '{config_file}' not found")
        return None

    config.read(str(config_path))

    # Check if section exists
    if section not in config:
        logger.warning(f"Section '{section}' not found in config file")
        return None

    # Extract credentials
    credentials = {
        'login': int(config[section].get('login', 0)),
        'password': config[section].get('password', ''),
        'server': config[section].get('server', ''),
    }

    # Optional: Add path if specified
    if 'path' in config[section]:
        credentials['path'] = config[section]['path']

    return credentials


def example_1_symbol_discovery():
    """Example 1: Discover available symbols"""
    print("\n" + "="*60)
    print("Example 1: Symbol Discovery")
    print("="*60)

    # Load credentials from config file
    credentials = get_credentials_from_config()
    if not credentials:
        print("ERROR: Could not load credentials from config.ini")
        return

    # Create client instance
    client = MT5Client()

    # Connect to MT5
    success = client.connect(
        login=credentials['login'],
        password=credentials['password'],
        server=credentials['server']
    )

    if not success:
        print("Failed to connect to MT5")
        return

    print("Connected to MT5 successfully!")

    try:
        # Create symbol instance
        symbol = MT5Symbol(client)

        # Get all available symbols
        print("\nGetting all available symbols...")
        all_symbols = symbol.get_symbols('all')
        print(f"Total symbols available: {len(all_symbols)}")
        print(f"First 10 symbols: {all_symbols[:10]}")

        # Get market watch symbols
        print("\nGetting Market Watch symbols...")
        market_watch = symbol.get_symbols('market_watch')
        print(f"Symbols in Market Watch: {len(market_watch)}")
        print(f"Market Watch symbols: {market_watch}")

        # Get symbols by group
        print("\nGetting Forex symbols...")
        forex_symbols = symbol.get_symbols('group', 'Forex*')
        print(f"Forex symbols found: {len(forex_symbols)}")
        print(f"First 10 Forex symbols: {forex_symbols[:10]}")

        # Search for specific symbols
        print("\nSearching for EUR symbols...")
        eur_symbols = symbol.get_symbols('search', 'EUR*')
        print(f"EUR symbols found: {len(eur_symbols)}")
        print(f"EUR symbols: {eur_symbols}")

    finally:
        # Always disconnect
        client.disconnect()
        print("\nDisconnected from MT5")


def example_2_symbol_information():
    """Example 2: Get symbol information"""
    print("\n" + "="*60)
    print("Example 2: Symbol Information")
    print("="*60)

    credentials = get_credentials_from_config()
    if not credentials:
        print("ERROR: Could not load credentials from config.ini")
        return

    client = MT5Client()

    if not client.connect(**credentials):
        print("Failed to connect to MT5")
        return

    print("Connected to MT5 successfully!")

    try:
        symbol = MT5Symbol(client)
        symbol_name = "EURUSD"

        # Get complete symbol information
        print(f"\nGetting complete info for {symbol_name}...")
        info = symbol.get_info(symbol_name)
        print(f"Symbol: {info['name']}")
        print(f"Description: {info['description']}")
        print(f"Bid: {info['bid']}")
        print(f"Ask: {info['ask']}")
        print(f"Spread: {info['spread']}")
        print(f"Digits: {info['digits']}")
        print(f"Point: {info['point']}")

        # Get specific attributes
        print(f"\nGetting specific attributes for {symbol_name}...")
        bid = symbol.get_info(symbol_name, 'bid')
        ask = symbol.get_info(symbol_name, 'ask')
        print(f"Bid: {bid}")
        print(f"Ask: {ask}")

        # Get symbol summary
        print(f"\nGetting summary for {symbol_name}...")
        summary = symbol.get_summary(symbol_name)
        print(f"Summary: {summary}")

    finally:
        client.disconnect()
        print("\nDisconnected from MT5")


def example_3_market_watch_management():
    """Example 3: Manage Market Watch"""
    print("\n" + "="*60)
    print("Example 3: Market Watch Management")
    print("="*60)

    credentials = get_credentials_from_config()
    if not credentials:
        print("ERROR: Could not load credentials from config.ini")
        return

    client = MT5Client()

    if not client.connect(**credentials):
        print("Failed to connect to MT5")
        return

    print("Connected to MT5 successfully!")

    try:
        symbol = MT5Symbol(client)
        test_symbol = "GBPUSD"

        # Initialize symbol for trading
        print(f"\nInitializing symbol {test_symbol}...")
        success = symbol.initialize(test_symbol)
        print(f"Initialize result: {success}")

        # Add symbol to Market Watch
        print(f"\nAdding {test_symbol} to Market Watch...")
        success = symbol.manage('add', test_symbol)
        print(f"Add result: {success}")

        # Check if symbol is visible
        is_visible = symbol.check(test_symbol, 'visible')
        print(f"{test_symbol} visible in Market Watch: {is_visible}")

        # Remove symbol from Market Watch
        print(f"\nRemoving {test_symbol} from Market Watch...")
        success = symbol.manage('remove', test_symbol)
        print(f"Remove result: {success}")

    finally:
        client.disconnect()
        print("\nDisconnected from MT5")


def example_4_symbol_status_checks():
    """Example 4: Check symbol status"""
    print("\n" + "="*60)
    print("Example 4: Symbol Status Checks")
    print("="*60)

    credentials = get_credentials_from_config()
    if not credentials:
        print("ERROR: Could not load credentials from config.ini")
        return

    client = MT5Client()

    if not client.connect(**credentials):
        print("Failed to connect to MT5")
        return

    print("Connected to MT5 successfully!")

    try:
        symbol = MT5Symbol(client)
        test_symbol = "EURUSD"

        print(f"\nChecking status for {test_symbol}...")

        # Check if symbol is available
        is_available = symbol.check(test_symbol, 'available')
        print(f"Available: {is_available}")

        # Check if symbol is visible
        is_visible = symbol.check(test_symbol, 'visible')
        print(f"Visible: {is_visible}")

        # Check if symbol is tradable
        is_tradable = symbol.check(test_symbol, 'tradable')
        print(f"Tradable: {is_tradable}")

        # Check if market is open
        is_market_open = symbol.check(test_symbol, 'market_open')
        print(f"Market Open: {is_market_open}")

    finally:
        client.disconnect()
        print("\nDisconnected from MT5")


def example_5_real_time_prices():
    """Example 5: Get real-time prices"""
    print("\n" + "="*60)
    print("Example 5: Real-Time Prices")
    print("="*60)

    credentials = get_credentials_from_config()
    if not credentials:
        print("ERROR: Could not load credentials from config.ini")
        return

    client = MT5Client()

    if not client.connect(**credentials):
        print("Failed to connect to MT5")
        return

    print("Connected to MT5 successfully!")

    try:
        symbol = MT5Symbol(client)
        test_symbol = "EURUSD"

        print(f"\nGetting prices for {test_symbol}...")

        # Get bid price
        bid = symbol.get_price(test_symbol, 'bid')
        print(f"Bid: {bid}")

        # Get ask price
        ask = symbol.get_price(test_symbol, 'ask')
        print(f"Ask: {ask}")

        # Get last price
        last = symbol.get_price(test_symbol, 'last')
        print(f"Last: {last}")

        # Get current prices (bid, ask, spread)
        current = symbol.get_price(test_symbol, 'current')
        print(f"\nCurrent prices:")
        print(f"  Bid: {current['bid']}")
        print(f"  Ask: {current['ask']}")
        print(f"  Spread: {current['spread']}")
        print(f"  Time: {current['time']}")

    finally:
        client.disconnect()
        print("\nDisconnected from MT5")


def example_6_volume_validation():
    """Example 6: Validate trading volumes"""
    print("\n" + "="*60)
    print("Example 6: Volume Validation")
    print("="*60)

    credentials = get_credentials_from_config()
    if not credentials:
        print("ERROR: Could not load credentials from config.ini")
        return

    client = MT5Client()

    if not client.connect(**credentials):
        print("Failed to connect to MT5")
        return

    print("Connected to MT5 successfully!")

    try:
        symbol = MT5Symbol(client)
        test_symbol = "EURUSD"

        # Get symbol info to see volume constraints
        info = symbol.get_info(test_symbol)
        print(f"\nVolume constraints for {test_symbol}:")
        print(f"  Min volume: {info['volume_min']}")
        print(f"  Max volume: {info['volume_max']}")
        print(f"  Volume step: {info['volume_step']}")

        # Test various volumes
        test_volumes = [0.001, 0.01, 0.1, 1.0, 10.0, 200.0]

        print(f"\nValidating volumes for {test_symbol}:")
        for vol in test_volumes:
            is_valid, message = symbol.validate_volume(test_symbol, vol)
            status = "VALID" if is_valid else "INVALID"
            print(f"  Volume {vol:7.3f}: {status:7s} - {message}")

        # Validate symbol existence
        print("\nValidating symbol existence...")
        is_valid, message = symbol.validate("EURUSD", "exists")
        print(f"EURUSD: {message}")

        is_valid, message = symbol.validate("INVALID_SYMBOL", "exists")
        print(f"INVALID_SYMBOL: {message}")

        # Validate symbol is tradable
        print("\nValidating symbol tradability...")
        is_valid, message = symbol.validate("EURUSD", "tradable")
        print(f"EURUSD: {message}")

    finally:
        client.disconnect()
        print("\nDisconnected from MT5")


def example_7_market_depth():
    """Example 7: Get market depth (DOM)"""
    print("\n" + "="*60)
    print("Example 7: Market Depth (DOM)")
    print("="*60)

    credentials = get_credentials_from_config()
    if not credentials:
        print("ERROR: Could not load credentials from config.ini")
        return

    client = MT5Client()

    if not client.connect(**credentials):
        print("Failed to connect to MT5")
        return

    print("Connected to MT5 successfully!")

    try:
        symbol = MT5Symbol(client)
        test_symbol = "EURUSD"

        # Subscribe to market depth
        print(f"\nSubscribing to market depth for {test_symbol}...")
        success = symbol.subscribe(test_symbol)
        print(f"Subscribe result: {success}")

        # Get market depth
        print(f"\nGetting market depth for {test_symbol}...")
        depth = symbol.get_depth(test_symbol)

        if depth:
            print(f"Market depth entries: {len(depth)}")
            print("\nFirst 5 entries:")
            for i, entry in enumerate(depth[:5], 1):
                entry_type = "BUY" if entry['type'] == 1 else "SELL"
                print(f"{i}. Type: {entry_type:4s}, Price: {entry['price']:.5f}, Volume: {entry['volume']}")
        else:
            print("No market depth available")

        # Unsubscribe from market depth
        print(f"\nUnsubscribing from market depth for {test_symbol}...")
        success = symbol.unsubscribe(test_symbol)
        print(f"Unsubscribe result: {success}")

    finally:
        client.disconnect()
        print("\nDisconnected from MT5")


def example_8_export_symbols():
    """Example 8: Export symbol list"""
    print("\n" + "="*60)
    print("Example 8: Export Symbol List")
    print("="*60)

    credentials = get_credentials_from_config()
    if not credentials:
        print("ERROR: Could not load credentials from config.ini")
        return

    client = MT5Client()

    if not client.connect(**credentials):
        print("Failed to connect to MT5")
        return

    print("Connected to MT5 successfully!")

    try:
        symbol = MT5Symbol(client)

        # Export market watch symbols as dict
        print("\nExporting Market Watch symbols as dict...")
        symbols_dict = symbol.export_list(format='dict')
        print(f"Exported {len(symbols_dict)} symbols")
        if len(symbols_dict) > 0:
            print(f"First symbol: {symbols_dict[0]['name']}")

        # Export specific symbols as JSON
        print("\nExporting specific symbols as JSON...")
        symbols_to_export = ['EURUSD', 'GBPUSD', 'USDJPY']
        json_data = symbol.export_list(symbols_to_export, format='json')
        print(f"JSON data (first 200 chars):\n{json_data[:200]}...")

        # Export to JSON file
        print("\nExporting to JSON file...")
        result = symbol.export_list(symbols_to_export, format='json', filepath='symbols.json')
        print(result)

        # Export to CSV file
        print("\nExporting to CSV file...")
        result = symbol.export_list(symbols_to_export, format='csv', filepath='symbols.csv')
        print(result)

    finally:
        client.disconnect()
        print("\nDisconnected from MT5")


def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("MT5 SYMBOL MANAGEMENT EXAMPLES")
    print("="*60)

    try:
        # Run examples
        example_1_symbol_discovery()
        example_2_symbol_information()
        example_3_market_watch_management()
        example_4_symbol_status_checks()
        example_5_real_time_prices()
        example_6_volume_validation()
        example_7_market_depth()
        example_8_export_symbols()

        print("\n" + "="*60)
        print("ALL EXAMPLES COMPLETED")
        print("="*60)

    except Exception as e:
        logger.error(f"Error running examples: {e}", exc_info=True)
        print(f"\nERROR: {e}")


if __name__ == "__main__":
    main()
