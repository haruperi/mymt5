"""
MT5Terminal Usage Examples

This module demonstrates various ways to use the MT5Terminal class
for retrieving terminal information, checking status, and performing diagnostics.
"""

import sys
import os
from pathlib import Path

# Add project root to Python path to allow imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mylogger import logger
from mymt5.client import MT5Client
from mymt5.terminal import MT5Terminal
import configparser


logger.info("Loading terminal info examples")


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


def example_1_terminal_information():
    """Example 1: Get terminal information"""
    print("\n" + "="*60)
    print("Example 1: Terminal Information")
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
        # Create terminal instance
        terminal = MT5Terminal(client)

        # Get complete terminal information
        print("\nGetting complete terminal information...")
        info = terminal.get()
        print(f"Name: {info['name']}")
        print(f"Company: {info['company']}")
        print(f"Build: {info['build']}")
        print(f"Language: {info['language']}")
        print(f"Path: {info['path']}")
        print(f"Data Path: {info['data_path']}")

        # Get specific attributes
        print("\nGetting specific attributes...")
        build = terminal.get('build')
        print(f"Build: {build}")

        name = terminal.get('name')
        print(f"Name: {name}")

        connected = terminal.get('connected')
        print(f"Connected: {connected}")

    finally:
        # Always disconnect
        client.disconnect()
        print("\nDisconnected from MT5")


def example_2_terminal_status():
    """Example 2: Check terminal status"""
    print("\n" + "="*60)
    print("Example 2: Terminal Status Checks")
    print("="*60)

    credentials = get_credentials_from_config()
    if not credentials:
        print("ERROR: Could not load credentials from config.ini")
        return

    client = MT5Client()

    # Extract only connection parameters (exclude 'path' which is for initialize, not connect)
    connect_params = {k: v for k, v in credentials.items() if k in ['login', 'password', 'server']}
    if not client.connect(**connect_params):
        print("Failed to connect to MT5")
        return

    print("Connected to MT5 successfully!")

    try:
        terminal = MT5Terminal(client)

        print("\nChecking terminal status...")

        # Check if terminal is connected to server
        is_connected = terminal.check('connected')
        print(f"Connected to server: {is_connected}")

        # Check if trading is allowed
        trade_allowed = terminal.check('trade_allowed')
        print(f"Trading allowed: {trade_allowed}")

        # Check if DLLs are allowed
        dlls_allowed = terminal.check('dlls_allowed')
        print(f"DLLs allowed: {dlls_allowed}")

        # Check if email is enabled
        email_enabled = terminal.check('email_enabled')
        print(f"Email enabled: {email_enabled}")

        # Check if push notifications are enabled
        notifications_enabled = terminal.check('notifications_enabled')
        print(f"Push notifications enabled: {notifications_enabled}")

        # Check if FTP is enabled
        ftp_enabled = terminal.check('ftp_enabled')
        print(f"FTP enabled: {ftp_enabled}")

        # Check if community connection is active
        community_connection = terminal.check('community_connection')
        print(f"Community connection: {community_connection}")

        # Check if trade API is disabled
        tradeapi_disabled = terminal.check('tradeapi_disabled')
        print(f"Trade API disabled: {tradeapi_disabled}")

    finally:
        client.disconnect()
        print("\nDisconnected from MT5")


def example_3_terminal_properties():
    """Example 3: Get terminal properties"""
    print("\n" + "="*60)
    print("Example 3: Terminal Properties")
    print("="*60)

    credentials = get_credentials_from_config()
    if not credentials:
        print("ERROR: Could not load credentials from config.ini")
        return

    client = MT5Client()

    # Extract only connection parameters (exclude 'path' which is for initialize, not connect)
    connect_params = {k: v for k, v in credentials.items() if k in ['login', 'password', 'server']}
    if not client.connect(**connect_params):
        print("Failed to connect to MT5")
        return

    print("Connected to MT5 successfully!")

    try:
        terminal = MT5Terminal(client)

        # Get resource properties
        print("\nGetting resource properties...")
        resources = terminal.get_properties('resources')
        print(f"Max bars: {resources['maxbars']}")
        print(f"Last ping: {resources['ping_last']} ms")
        print(f"Retransmission: {resources['retransmission']}%")
        print(f"Community balance: {resources['community_balance']}")

        # Get display properties
        print("\nGetting display properties...")
        display = terminal.get_properties('display')
        print(f"Name: {display['name']}")
        print(f"Company: {display['company']}")
        print(f"Language: {display['language']}")
        print(f"Build: {display['build']}")
        print(f"Code page: {display['codepage']}")

        # Get limit properties
        print("\nGetting limit properties...")
        limits = terminal.get_properties('limits')
        print(f"DLLs allowed: {limits['dlls_allowed']}")
        print(f"Trading allowed: {limits['trade_allowed']}")
        print(f"Trade API disabled: {limits['tradeapi_disabled']}")
        print(f"Max bars: {limits['maxbars']}")

        # Get all properties
        print("\nGetting all properties...")
        all_props = terminal.get_properties('all')
        print(f"Properties groups: {list(all_props.keys())}")

    finally:
        client.disconnect()
        print("\nDisconnected from MT5")


def example_4_terminal_summary():
    """Example 4: Get terminal summary"""
    print("\n" + "="*60)
    print("Example 4: Terminal Summary")
    print("="*60)

    credentials = get_credentials_from_config()
    if not credentials:
        print("ERROR: Could not load credentials from config.ini")
        return

    client = MT5Client()

    # Extract only connection parameters (exclude 'path' which is for initialize, not connect)
    connect_params = {k: v for k, v in credentials.items() if k in ['login', 'password', 'server']}
    if not client.connect(**connect_params):
        print("Failed to connect to MT5")
        return

    print("Connected to MT5 successfully!")

    try:
        terminal = MT5Terminal(client)

        # Get terminal summary
        print("\nGetting terminal summary...")
        summary = terminal.get_summary()

        print(f"\nTerminal Summary:")
        print(f"  Name: {summary['name']}")
        print(f"  Company: {summary['company']}")
        print(f"  Build: {summary['build']}")
        print(f"  Language: {summary['language']}")
        print(f"  Connected: {summary['connected']}")
        print(f"  Trade Allowed: {summary['trade_allowed']}")
        print(f"  Path: {summary['path']}")
        print(f"  Data Path: {summary['data_path']}")
        print(f"  Max Bars: {summary['maxbars']}")
        print(f"  Last Ping: {summary['ping_last']} ms")
        print(f"  DLLs Allowed: {summary['dlls_allowed']}")
        print(f"  Trade API Disabled: {summary['tradeapi_disabled']}")
        print(f"  Email Enabled: {summary['email_enabled']}")
        print(f"  Notifications Enabled: {summary['notifications_enabled']}")

    finally:
        client.disconnect()
        print("\nDisconnected from MT5")


def example_5_print_terminal_info():
    """Example 5: Print formatted terminal information"""
    print("\n" + "="*60)
    print("Example 5: Print Formatted Terminal Info")
    print("="*60)

    credentials = get_credentials_from_config()
    if not credentials:
        print("ERROR: Could not load credentials from config.ini")
        return

    client = MT5Client()

    # Extract only connection parameters (exclude 'path' which is for initialize, not connect)
    connect_params = {k: v for k, v in credentials.items() if k in ['login', 'password', 'server']}
    if not client.connect(**connect_params):
        print("Failed to connect to MT5")
        return

    print("Connected to MT5 successfully!")

    try:
        terminal = MT5Terminal(client)

        # Print formatted terminal information
        terminal.print_info()

    finally:
        client.disconnect()
        print("\nDisconnected from MT5")


def example_6_export_terminal_info():
    """Example 6: Export terminal information"""
    print("\n" + "="*60)
    print("Example 6: Export Terminal Information")
    print("="*60)

    credentials = get_credentials_from_config()
    if not credentials:
        print("ERROR: Could not load credentials from config.ini")
        return

    client = MT5Client()

    # Extract only connection parameters (exclude 'path' which is for initialize, not connect)
    connect_params = {k: v for k, v in credentials.items() if k in ['login', 'password', 'server']}
    if not client.connect(**connect_params):
        print("Failed to connect to MT5")
        return

    print("Connected to MT5 successfully!")

    try:
        terminal = MT5Terminal(client)

        # Export as dict
        print("\nExporting terminal info as dict...")
        info_dict = terminal.export('dict')
        print(f"Exported {len(info_dict)} fields")
        print(f"Sample fields: name={info_dict['name']}, build={info_dict['build']}")

        # Export as JSON
        print("\nExporting terminal info as JSON...")
        json_data = terminal.export('json')
        print(f"JSON data (first 200 chars):\n{json_data[:200]}...")

        # Export to JSON file
        print("\nExporting to JSON file...")
        result = terminal.export('json', 'terminal_info.json')
        print(result)

        # Export to CSV file
        print("\nExporting to CSV file...")
        result = terminal.export('csv', 'terminal_info.csv')
        print(result)

    finally:
        client.disconnect()
        print("\nDisconnected from MT5")


def example_7_compatibility_check():
    """Example 7: Check system compatibility"""
    print("\n" + "="*60)
    print("Example 7: System Compatibility Check")
    print("="*60)

    credentials = get_credentials_from_config()
    if not credentials:
        print("ERROR: Could not load credentials from config.ini")
        return

    client = MT5Client()

    # Extract only connection parameters (exclude 'path' which is for initialize, not connect)
    connect_params = {k: v for k, v in credentials.items() if k in ['login', 'password', 'server']}
    if not client.connect(**connect_params):
        print("Failed to connect to MT5")
        return

    print("Connected to MT5 successfully!")

    try:
        terminal = MT5Terminal(client)

        # Check system compatibility
        print("\nChecking system compatibility...")
        compatibility = terminal.check_compatibility()

        # Python information
        print("\nPython Information:")
        print(f"  Version: {compatibility['python']['version']}")
        print(f"  Major: {compatibility['python']['major']}")
        print(f"  Minor: {compatibility['python']['minor']}")
        print(f"  Micro: {compatibility['python']['micro']}")
        print(f"  Compatible: {compatibility['python']['compatible']}")

        # System information
        print("\nSystem Information:")
        print(f"  Platform: {compatibility['system']['platform']}")
        print(f"  Release: {compatibility['system']['platform_release']}")
        print(f"  Version: {compatibility['system']['platform_version']}")
        print(f"  Architecture: {compatibility['system']['architecture']}")
        print(f"  Processor: {compatibility['system']['processor']}")

        # MT5 information
        print("\nMT5 Information:")
        print(f"  Version: {compatibility['mt5']['version']}")
        print(f"  Build: {compatibility['mt5']['build']}")
        print(f"  Name: {compatibility['mt5']['name']}")
        print(f"  Company: {compatibility['mt5']['company']}")

        # Terminal status
        print("\nTerminal Status:")
        print(f"  Connected: {compatibility['terminal']['connected']}")
        print(f"  Trade Allowed: {compatibility['terminal']['trade_allowed']}")
        print(f"  DLLs Allowed: {compatibility['terminal']['dlls_allowed']}")
        print(f"  Trade API Disabled: {compatibility['terminal']['tradeapi_disabled']}")

        # Overall status
        print(f"\nOverall Compatibility Status:")
        print(f"  {compatibility['overall_status']}")

    finally:
        client.disconnect()
        print("\nDisconnected from MT5")


def example_8_terminal_diagnostics():
    """Example 8: Comprehensive terminal diagnostics"""
    print("\n" + "="*60)
    print("Example 8: Comprehensive Terminal Diagnostics")
    print("="*60)

    credentials = get_credentials_from_config()
    if not credentials:
        print("ERROR: Could not load credentials from config.ini")
        return

    client = MT5Client()

    # Extract only connection parameters (exclude 'path' which is for initialize, not connect)
    connect_params = {k: v for k, v in credentials.items() if k in ['login', 'password', 'server']}
    if not client.connect(**connect_params):
        print("Failed to connect to MT5")
        return

    print("Connected to MT5 successfully!")

    try:
        terminal = MT5Terminal(client)

        print("\n" + "-"*60)
        print("TERMINAL DIAGNOSTICS REPORT")
        print("-"*60)

        # Basic information
        summary = terminal.get_summary()
        print(f"\n1. Basic Information:")
        print(f"   Terminal: {summary['name']} (Build {summary['build']})")
        print(f"   Company: {summary['company']}")
        print(f"   Language: {summary['language']}")

        # Connection status
        print(f"\n2. Connection Status:")
        print(f"   Connected to Server: {'YES' if summary['connected'] else 'NO'}")
        print(f"   Last Ping: {summary['ping_last']} ms")

        # Trading status
        print(f"\n3. Trading Status:")
        print(f"   Trading Allowed: {'YES' if summary['trade_allowed'] else 'NO'}")
        print(f"   Trade API: {'DISABLED' if summary['tradeapi_disabled'] else 'ENABLED'}")
        print(f"   DLLs Allowed: {'YES' if summary['dlls_allowed'] else 'NO'}")

        # Notifications
        print(f"\n4. Notification Settings:")
        print(f"   Email: {'ENABLED' if summary['email_enabled'] else 'DISABLED'}")
        print(f"   Push: {'ENABLED' if summary['notifications_enabled'] else 'DISABLED'}")

        # Resources
        resources = terminal.get_properties('resources')
        print(f"\n5. Resource Information:")
        print(f"   Max Bars: {resources['maxbars']}")
        print(f"   Retransmission: {resources['retransmission']}%")

        # Paths
        print(f"\n6. Installation Paths:")
        print(f"   Terminal: {summary['path']}")
        print(f"   Data: {summary['data_path']}")

        # Compatibility check
        compatibility = terminal.check_compatibility()
        print(f"\n7. Compatibility:")
        print(f"   Python Version: {compatibility['python']['major']}.{compatibility['python']['minor']}.{compatibility['python']['micro']}")
        print(f"   Python Compatible: {'YES' if compatibility['python']['compatible'] else 'NO'}")
        print(f"   System: {compatibility['system']['platform']} {compatibility['system']['platform_release']}")
        print(f"   Overall Status: {compatibility['overall_status']}")

        print("\n" + "-"*60)
        print("DIAGNOSTICS COMPLETE")
        print("-"*60)

    finally:
        client.disconnect()
        print("\nDisconnected from MT5")


def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("MT5 TERMINAL INFORMATION EXAMPLES")
    print("="*60)

    try:
        # Run examples
        example_1_terminal_information()
        example_2_terminal_status()
        example_3_terminal_properties()
        example_4_terminal_summary()
        example_5_print_terminal_info()
        example_6_export_terminal_info()
        example_7_compatibility_check()
        example_8_terminal_diagnostics()

        print("\n" + "="*60)
        print("ALL EXAMPLES COMPLETED")
        print("="*60)

    except Exception as e:
        logger.error(f"Error running examples: {e}", exc_info=True)
        print(f"\nERROR: {e}")


if __name__ == "__main__":
    main()
