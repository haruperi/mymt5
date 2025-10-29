"""
MT5Client Usage Examples

This module demonstrates various ways to use the MT5Client class
for connecting to and managing MetaTrader 5 terminal connections.
"""

import sys
import os
from pathlib import Path

# Add project root to Python path to allow imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mylogger import logger
from mymt5.client import MT5Client
import configparser


logger.info("Loading client_example module")


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


def example_basic_connection():
    """Example 1: Basic connection to MT5."""
    print("\n" + "="*60)
    print("Example 1: Basic Connection")
    print("="*60)

    # Load credentials from config
    credentials = get_credentials_from_config()
    if not credentials:
        print("ERROR: Could not load credentials from config.ini")
        return

    # Create client instance
    client = MT5Client()

    # Initialize and connect with credentials
    success = client.initialize(
        login=credentials['login'],
        password=credentials['password'],
        server=credentials['server']
    )

    if success:
        print("✓ Connected successfully!")
        print(f"  Connection state: {client.connection_state}")
        print(f"  Account: {client.account_login}")
        print(f"  Server: {client.account_server}")
    else:
        print("✗ Connection failed!")
        error = client.get_error()
        if error:
            print(f"  Error: {error}")

    # Cleanup
    client.shutdown()


def example_connection_from_config():
    """Example 2: Connect using configuration file."""
    print("\n" + "="*60)
    print("Example 2: Connection from Config File")
    print("="*60)

    # Load credentials from config
    credentials = get_credentials_from_config()
    if not credentials:
        print("ERROR: Could not load credentials from config.ini")
        return

    # Read config for additional settings
    config = configparser.ConfigParser()
    config_path = Path('config.ini')
    if not config_path.exists():
        project_root = Path(__file__).parent.parent
        config_path = project_root / 'config.ini'
    config.read(str(config_path))

    if 'MT5' in config:

        client = MT5Client(
            path=credentials.get('path'),
            timeout=30000
        )

        success = client.initialize(
            login=credentials['login'],
            password=credentials['password'],
            server=credentials['server']
        )

        if success:
            print("✓ Connected using config file!")
            status = client.get_status()
            print(f"  Terminal connected: {status['terminal_info']['connected']}")
            print(f"  Account login: {status['account_info']['login']}")
        else:
            print("✗ Connection failed!")

        client.shutdown()
    else:
        print("✗ MT5 section not found in config.ini")


def example_context_manager():
    """Example 3: Using client as context manager."""
    print("\n" + "="*60)
    print("Example 3: Context Manager")
    print("="*60)

    # Load credentials from config
    credentials = get_credentials_from_config()
    if not credentials:
        print("ERROR: Could not load credentials from config.ini")
        return

    # Client automatically shuts down when exiting context
    with MT5Client() as client:
        if client.initialize(
            login=credentials['login'],
            password=credentials['password'],
            server=credentials['server']
        ):
            print("✓ Connected within context manager")
            print(f"  Is connected: {client.is_connected()}")
            print(f"  Ping successful: {client.ping()}")
        else:
            print("✗ Connection failed")

    print("✓ Client automatically shut down")


def example_auto_reconnection():
    """Example 4: Auto-reconnection setup."""
    print("\n" + "="*60)
    print("Example 4: Auto-Reconnection")
    print("="*60)

    client = MT5Client()

    # Enable auto-reconnection
    client.enable_auto_reconnect(
        retry_attempts=5,
        retry_delay=10
    )

    print(f"✓ Auto-reconnect enabled")
    print(f"  Retry attempts: {client.retry_attempts}")
    print(f"  Retry delay: {client.retry_delay}s")

    # Load credentials from config
    credentials = get_credentials_from_config()
    if not credentials:
        print("ERROR: Could not load credentials from config.ini")
        return

    # Connect
    if client.initialize(
        login=credentials['login'],
        password=credentials['password'],
        server=credentials['server']
    ):
        print("✓ Connected with auto-reconnect enabled")

        # If connection drops, client will auto-reconnect
        # You can also manually trigger reconnection
        # client.reconnect()

    client.shutdown()


def example_event_callbacks():
    """Example 5: Using event callbacks."""
    print("\n" + "="*60)
    print("Example 5: Event Callbacks")
    print("="*60)

    def on_connect(**kwargs):
        """Called when client connects."""
        print("  📡 Event: Connected to MT5")

    def on_disconnect(**kwargs):
        """Called when client disconnects."""
        print("  📡 Event: Disconnected from MT5")

    def on_error(**kwargs):
        """Called when an error occurs."""
        error = kwargs.get('error')
        print(f"  ⚠️  Event: Error occurred - {error}")

    # Create client and register callbacks
    client = MT5Client()
    client.on('connect', on_connect)
    client.on('disconnect', on_disconnect)
    client.on('error', on_error)

    print("✓ Event callbacks registered")

    # Load credentials from config
    credentials = get_credentials_from_config()
    if not credentials:
        print("ERROR: Could not load credentials from config.ini")
        return

    # Events will be triggered automatically
    if client.initialize(
        login=credentials['login'],
        password=credentials['password'],
        server=credentials['server']
    ):
        print("✓ Connection established (connect event should fire)")

    client.disconnect()
    print("✓ Disconnected (disconnect event should fire)")

    client.shutdown()


def example_multi_account():
    """Example 6: Multi-account management."""
    print("\n" + "="*60)
    print("Example 6: Multi-Account Management")
    print("="*60)

    client = MT5Client()

    # Load credentials from config
    credentials = get_credentials_from_config()
    if not credentials:
        print("ERROR: Could not load credentials from config.ini")
        return

    # Save multiple accounts
    client.save_account(
        'demo_account',
        credentials['login'],
        credentials['password'],
        credentials['server']
    )

    print("✓ Saved demo account")

    # List all saved accounts
    accounts = client.list_accounts()
    print(f"✓ Saved accounts: {accounts}")

    # Switch to saved account
    if client.switch_account('demo_account'):
        print(f"✓ Switched to: {client.current_account}")
        print(f"  Account login: {client.account_login}")
        print(f"  Server: {client.account_server}")
    else:
        print("✗ Failed to switch account")

    client.shutdown()


def example_configuration():
    """Example 7: Configuration management."""
    print("\n" + "="*60)
    print("Example 7: Configuration Management")
    print("="*60)

    client = MT5Client()

    # Configure client settings
    client.configure(
        timeout=30000,
        auto_reconnect_enabled=True,
        retry_attempts=5,
        retry_delay=10
    )

    print("✓ Client configured")

    # Get configuration
    config = client.get_config()
    print(f"  Timeout: {config['timeout']}ms")
    print(f"  Auto-reconnect: {config['auto_reconnect_enabled']}")
    print(f"  Retry attempts: {config['retry_attempts']}")

    # Save configuration to file
    client.save_config('examples/client_config.json')
    print("✓ Configuration saved to file")

    # Load configuration from file
    new_client = MT5Client()
    new_client.load_config('examples/client_config.json')
    print("✓ Configuration loaded from file")

    client.shutdown()
    new_client.shutdown()


def example_status_diagnostics():
    """Example 8: Status and diagnostics."""
    print("\n" + "="*60)
    print("Example 8: Status and Diagnostics")
    print("="*60)

    client = MT5Client()

    # Load credentials from config
    credentials = get_credentials_from_config()
    if not credentials:
        print("ERROR: Could not load credentials from config.ini")
        return

    if client.initialize(
        login=credentials['login'],
        password=credentials['password'],
        server=credentials['server']
    ):
        # Get comprehensive status
        status = client.get_status()

        print("✓ Client Status:")
        print(f"  Connection state: {status['connection_state']}")
        print(f"  Is connected: {status['is_connected']}")
        print(f"  Account: {status['account_info']['login']}")
        print(f"  Server: {status['account_info']['server']}")

        # Get connection statistics
        stats = client.get_connection_statistics()

        print("\n✓ Connection Statistics:")
        print(f"  Total attempts: {stats['total_attempts']}")
        print(f"  Successful: {stats['successful_connections']}")
        print(f"  Failed: {stats['failed_connections']}")
        print(f"  Success rate: {stats['success_rate']:.1%}")

        # Export logs
        client.export_logs('examples/client_logs.json')
        print("\n✓ Logs exported to file")

    client.shutdown()


def example_error_handling():
    """Example 9: Error handling."""
    print("\n" + "="*60)
    print("Example 9: Error Handling")
    print("="*60)

    client = MT5Client()

    # Attempt connection with invalid credentials
    success = client.initialize(
        login=99999,
        password="invalid",
        server="InvalidServer"
    )

    if not success:
        print("✗ Connection failed (expected)")

        # Get last error
        error = client.get_error()
        if error:
            error_code, error_message = error
            print(f"  Error code: {error_code}")
            print(f"  Error message: {error_message}")

        # Get connection statistics
        stats = client.get_connection_statistics()
        print(f"  Total errors: {stats['error_count']}")

    client.shutdown()


def example_complete_workflow():
    """Example 10: Complete workflow."""
    print("\n" + "="*60)
    print("Example 10: Complete Workflow")
    print("="*60)

    # 1. Create client with configuration
    client = MT5Client(timeout=30000)

    # 2. Enable auto-reconnection
    client.enable_auto_reconnect(retry_attempts=3, retry_delay=5)

    # 3. Register event callbacks
    def on_connect(**kwargs):
        print("  → Connected")

    def on_error(**kwargs):
        error = kwargs.get('error')
        print(f"  → Error: {error}")

    client.on('connect', on_connect)
    client.on('error', on_error)

    # 4. Load credentials from config
    credentials = get_credentials_from_config()
    if not credentials:
        print("ERROR: Could not load credentials from config.ini")
        return

    # Save account credentials
    client.save_account(
        'my_demo',
        credentials['login'],
        credentials['password'],
        credentials['server']
    )

    # 5. Connect using saved account
    print("\n1. Connecting...")
    if client.switch_account('my_demo'):
        # 6. Check status
        print("\n2. Checking status...")
        status = client.get_status()
        print(f"   Connected: {status['is_connected']}")
        print(f"   Account: {status['account_info']['login']}")

        # 7. Get statistics
        print("\n3. Getting statistics...")
        stats = client.get_connection_statistics()
        print(f"   Success rate: {stats['success_rate']:.1%}")

        # 8. Export logs
        print("\n4. Exporting logs...")
        client.export_logs('examples/complete_workflow_logs.json')
        print("   ✓ Logs exported")

        # 9. Save configuration
        print("\n5. Saving configuration...")
        client.save_config('examples/complete_workflow_config.json')
        print("   ✓ Configuration saved")

    # 10. Cleanup
    print("\n6. Shutting down...")
    client.shutdown()
    print("   ✓ Client shutdown complete")


def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("MT5Client Usage Examples")
    print("="*60)

    try:
        example_basic_connection()
        example_connection_from_config()
        example_context_manager()
        example_auto_reconnection()
        example_event_callbacks()
        example_multi_account()
        example_configuration()
        example_status_diagnostics()
        example_error_handling()
        example_complete_workflow()

        print("\n" + "="*60)
        print("All examples completed!")
        print("="*60 + "\n")

    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
