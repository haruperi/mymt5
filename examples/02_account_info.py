"""
MT5Account Usage Examples

This example demonstrates all features of the MT5Account class:
- Getting account information
- Checking account status
- Calculating account metrics
- Validating credentials
- Getting account summary
- Exporting account data
"""

from mylogger import logger
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mymt5.client import MT5Client
from mymt5.account import MT5Account
import configparser


def example_01_basic_account_info():
    """Example 1: Getting basic account information"""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Getting Basic Account Information")
    print("=" * 70)

    # Create client and connect
    client = MT5Client()

    # Load credentials
    config = configparser.ConfigParser()
    config.read('config.ini')

    login = int(config['MT5']['login'])
    password = config['MT5']['password']
    server = config['MT5']['server']

    if not client.connect(login, password, server):
        print("Failed to connect to MT5")
        return

    # Create account instance
    account = MT5Account(client)

    # Get all account info
    print("\nGetting all account info...")
    info = account.get()
    print(f"Login: {info['login']}")
    print(f"Server: {info['server']}")
    print(f"Balance: ${info['balance']:.2f}")
    print(f"Equity: ${info['equity']:.2f}")
    print(f"Margin: ${info['margin']:.2f}")
    print(f"Free Margin: ${info['margin_free']:.2f}")
    print(f"Leverage: 1:{info['leverage']}")
    print(f"Currency: {info['currency']}")

    # Get specific attributes
    print("\nGetting specific attributes...")
    balance = account.get('balance')
    equity = account.get('equity')
    profit = account.get('profit')

    print(f"Balance: ${balance:.2f}")
    print(f"Equity: ${equity:.2f}")
    print(f"Profit: ${profit:.2f}")

    client.disconnect()


def example_02_account_status():
    """Example 2: Checking account status"""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Checking Account Status")
    print("=" * 70)

    client = MT5Client()
    config = configparser.ConfigParser()
    config.read('config.ini')

    if not client.connect(
        int(config['MT5']['login']),
        config['MT5']['password'],
        config['MT5']['server']
    ):
        print("Failed to connect to MT5")
        return

    account = MT5Account(client)

    # Check various statuses
    print("\nChecking account statuses...")

    is_demo = account.check('demo')
    print(f"Is Demo Account: {is_demo}")

    is_authorized = account.check('authorized')
    print(f"Is Authorized: {is_authorized}")

    trade_allowed = account.check('trade_allowed')
    print(f"Trading Allowed: {trade_allowed}")

    expert_allowed = account.check('expert_allowed')
    print(f"Expert Advisors Allowed: {expert_allowed}")

    client.disconnect()


def example_03_account_metrics():
    """Example 3: Calculating account metrics"""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Calculating Account Metrics")
    print("=" * 70)

    client = MT5Client()
    config = configparser.ConfigParser()
    config.read('config.ini')

    if not client.connect(
        int(config['MT5']['login']),
        config['MT5']['password'],
        config['MT5']['server']
    ):
        print("Failed to connect to MT5")
        return

    account = MT5Account(client)

    # Calculate margin level
    print("\nCalculating margin level...")
    margin_level = account.calculate('margin_level')
    print(f"Margin Level: {margin_level:.2f}%")

    if margin_level > 200:
        print("Status: Excellent - Very safe margin level")
    elif margin_level > 100:
        print("Status: Good - Healthy margin level")
    elif margin_level > 50:
        print("Status: Warning - Monitor margin carefully")
    else:
        print("Status: Critical - Risk of margin call!")

    # Calculate drawdown
    print("\nCalculating drawdown...")
    drawdown_percent = account.calculate('drawdown', type='percent')
    drawdown_absolute = account.calculate('drawdown', type='absolute')

    print(f"Drawdown (Percent): {drawdown_percent:.2f}%")
    print(f"Drawdown (Absolute): ${drawdown_absolute:.2f}")

    # Get comprehensive health metrics
    print("\nCalculating comprehensive health metrics...")
    health = account.calculate('health')

    print(f"\nAccount Health Report:")
    print(f"  Balance: ${health['balance']:.2f}")
    print(f"  Equity: ${health['equity']:.2f}")
    print(f"  Profit: ${health['profit']:.2f}")
    print(f"  Margin: ${health['margin']:.2f}")
    print(f"  Free Margin: ${health['margin_free']:.2f}")
    print(f"  Margin Level: {health['margin_level']:.2f}%")
    print(f"  Drawdown: {health['drawdown_percent']:.2f}%")
    print(f"  Health Status: {health['health_status'].upper()}")

    # Calculate margin required for a trade
    print("\nCalculating margin required for trades...")
    try:
        margin_eurusd = account.calculate('margin_required', symbol='EURUSD', volume=1.0)
        print(f"Margin required for 1.0 lot EURUSD: ${margin_eurusd:.2f}")

        margin_gbpusd = account.calculate('margin_required', symbol='GBPUSD', volume=0.5)
        print(f"Margin required for 0.5 lot GBPUSD: ${margin_gbpusd:.2f}")
    except Exception as e:
        print(f"Could not calculate margin required: {e}")

    client.disconnect()


def example_04_account_summary():
    """Example 4: Getting account summary"""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Getting Account Summary")
    print("=" * 70)

    client = MT5Client()
    config = configparser.ConfigParser()
    config.read('config.ini')

    if not client.connect(
        int(config['MT5']['login']),
        config['MT5']['password'],
        config['MT5']['server']
    ):
        print("Failed to connect to MT5")
        return

    account = MT5Account(client)

    # Get account summary
    print("\nGetting account summary...")
    summary = account.get_summary()

    print(f"\n{'ACCOUNT SUMMARY':^60}")
    print("=" * 60)
    print(f"{'Account Information':^60}")
    print("-" * 60)
    print(f"  Login:           {summary['login']}")
    print(f"  Name:            {summary['name']}")
    print(f"  Server:          {summary['server']}")
    print(f"  Company:         {summary['company']}")
    print(f"  Type:            {summary['trade_mode']}")
    print(f"  Currency:        {summary['currency']}")
    print(f"  Leverage:        1:{summary['leverage']}")
    print(f"\n{'Financial Information':^60}")
    print("-" * 60)
    print(f"  Balance:         ${summary['balance']:,.2f}")
    print(f"  Equity:          ${summary['equity']:,.2f}")
    print(f"  Profit:          ${summary['profit']:,.2f}")
    print(f"  Margin:          ${summary['margin']:,.2f}")
    print(f"  Free Margin:     ${summary['margin_free']:,.2f}")
    print(f"  Margin Level:    {summary['margin_level']:.2f}%")
    print(f"\n{'Status':^60}")
    print("-" * 60)
    print(f"  Trading Allowed: {summary['trade_allowed']}")
    print(f"  Health Status:   {summary['health_status'].upper()}")
    print("=" * 60)

    client.disconnect()


def example_05_export_data():
    """Example 5: Exporting account data"""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Exporting Account Data")
    print("=" * 70)

    client = MT5Client()
    config = configparser.ConfigParser()
    config.read('config.ini')

    if not client.connect(
        int(config['MT5']['login']),
        config['MT5']['password'],
        config['MT5']['server']
    ):
        print("Failed to connect to MT5")
        return

    account = MT5Account(client)

    # Export as dictionary
    print("\nExporting as dictionary...")
    data_dict = account.export('dict')
    print(f"Exported {len(data_dict)} fields")

    # Export as JSON string
    print("\nExporting as JSON string...")
    json_str = account.export('json')
    print(f"JSON length: {len(json_str)} characters")
    print("First 200 characters:")
    print(json_str[:200] + "...")

    # Export as JSON file
    print("\nExporting to JSON file...")
    result = account.export('json', 'data/account_info.json')
    print(result)

    # Export as CSV file
    print("\nExporting to CSV file...")
    result = account.export('csv', 'data/account_info.csv')
    print(result)

    client.disconnect()


def example_06_complete_workflow():
    """Example 6: Complete account management workflow"""
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Complete Account Management Workflow")
    print("=" * 70)

    # Initialize and connect
    print("\n1. Initializing and connecting...")
    client = MT5Client()
    config = configparser.ConfigParser()
    config.read('config.ini')

    if not client.connect(
        int(config['MT5']['login']),
        config['MT5']['password'],
        config['MT5']['server']
    ):
        print("Failed to connect to MT5")
        return

    account = MT5Account(client)
    print("   Connected successfully!")

    # Check account status
    print("\n2. Checking account status...")
    if account.check('trade_allowed'):
        print("   Trading is ALLOWED")
    else:
        print("   Trading is NOT allowed")

    # Get account balance
    print("\n3. Getting account balance...")
    balance = account.get('balance')
    equity = account.get('equity')
    print(f"   Balance: ${balance:.2f}")
    print(f"   Equity: ${equity:.2f}")

    # Calculate health
    print("\n4. Calculating account health...")
    health = account.calculate('health')
    print(f"   Health Status: {health['health_status'].upper()}")
    print(f"   Margin Level: {health['margin_level']:.2f}%")

    # Check if we can place a trade
    print("\n5. Checking margin for potential trade...")
    try:
        required_margin = account.calculate('margin_required', symbol='EURUSD', volume=0.1)
        free_margin = account.get('margin_free')

        print(f"   Required margin for 0.1 lot EURUSD: ${required_margin:.2f}")
        print(f"   Available free margin: ${free_margin:.2f}")

        if free_margin >= required_margin:
            print("   ✓ Sufficient margin available for trade")
        else:
            print("   ✗ Insufficient margin for trade")
    except Exception as e:
        print(f"   Could not calculate margin: {e}")

    # Generate summary report
    print("\n6. Generating summary report...")
    summary = account.get_summary()
    print(f"   Account: {summary['name']} ({summary['login']})")
    print(f"   Balance: ${summary['balance']:.2f}")
    print(f"   Health: {summary['health_status'].upper()}")

    # Export for records
    print("\n7. Exporting account snapshot...")
    account.export('json', 'data/account_snapshot.json')
    print("   Snapshot saved to data/account_snapshot.json")

    # Disconnect
    print("\n8. Disconnecting...")
    client.disconnect()
    print("   Disconnected successfully!")


def main():
    """Run all examples"""
    logger.info("Starting 02_account_management examples")

    try:
        example_01_basic_account_info()
        example_02_account_status()
        example_03_account_metrics()
        example_04_account_summary()
        example_05_export_data()
        example_06_complete_workflow()

        print("\n" + "=" * 70)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("=" * 70)

    except Exception as e:
        logger.error(f"Error in examples: {e}", exc_info=True)
        print(f"\nError: {e}")


if __name__ == "__main__":
    main()
