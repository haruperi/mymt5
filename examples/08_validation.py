from mylogger import logger
"""
MT5Validator Usage Examples

This example demonstrates comprehensive usage of the MT5Validator class for:
- Validating trading parameters (symbols, volumes, prices)
- Validating stop loss and take profit levels
- Validating order types and timeframes
- Validating complete trade requests
- Batch validation operations
- Managing validation rules
"""

from mymt5.client import MT5Client
from mymt5.validator import MT5Validator
from mymt5.enums import OrderType, TimeFrame
from datetime import datetime, timedelta
import MetaTrader5 as mt5
import configparser
from pathlib import Path


def get_credentials_from_config(config_file='config.ini', section='DEMO'):
    """Load MT5 credentials from config file."""
    config = configparser.ConfigParser()
    
    # Resolve config file path
    config_path = Path(config_file)
    if not config_path.exists():
        project_root = Path(__file__).parent.parent
        config_path = project_root / config_file
    
    if not config_path.exists():
        logger.warning(f"Config file '{config_file}' not found")
        return None
    
    config.read(str(config_path))
    
    if section not in config:
        logger.warning(f"Section '{section}' not found in {config_file}")
        return None
    
    section_config = config[section]
    
    credentials = {
        'login': int(section_config.get('login')),
        'password': section_config.get('password'),
        'server': section_config.get('server')
    }
    
    return credentials


def example1_basic_validation():
    """Example 1: Basic parameter validation."""
    print("\n" + "="*60)
    print("Example 1: Basic Parameter Validation")
    print("="*60)

    creds = get_credentials_from_config()
    if not creds:
        print("✗ Failed to load credentials from config.ini")
        return

    client = MT5Client()
    client.initialize(login=creds['login'], password=creds['password'], server=creds['server'])

    validator = MT5Validator(client=client)

    # Validate symbol
    print("\n1. Symbol Validation:")
    valid, msg = validator.validate('symbol', 'EURUSD')
    print(f"  EURUSD: {'✓ Valid' if valid else '✗ Invalid'} - {msg}")

    valid, msg = validator.validate('symbol', 'INVALID_SYMBOL')
    print(f"  INVALID_SYMBOL: {'✓ Valid' if valid else '✗ Invalid'} - {msg}")

    # Validate volume
    print("\n2. Volume Validation:")
    valid, msg = validator.validate('volume', 0.1, symbol='EURUSD')
    print(f"  0.1 lots: {'✓ Valid' if valid else '✗ Invalid'} - {msg}")

    valid, msg = validator.validate('volume', -0.1, symbol='EURUSD')
    print(f"  -0.1 lots: {'✓ Valid' if valid else '✗ Invalid'} - {msg}")

    # Validate price
    print("\n3. Price Validation:")
    valid, msg = validator.validate('price', 1.1000, symbol='EURUSD')
    print(f"  1.1000: {'✓ Valid' if valid else '✗ Invalid'} - {msg}")

    valid, msg = validator.validate('price', -1.0, symbol='EURUSD')
    print(f"  -1.0: {'✓ Valid' if valid else '✗ Invalid'} - {msg}")

    client.disconnect()


def example2_stop_loss_take_profit():
    """Example 2: Stop loss and take profit validation."""
    print("\n" + "="*60)
    print("Example 2: Stop Loss and Take Profit Validation")
    print("="*60)

    creds = get_credentials_from_config()
    if not creds:
        print("✗ Failed to load credentials from config.ini")
        return

    client = MT5Client()
    client.initialize(login=creds['login'], password=creds['password'], server=creds['server'])

    validator = MT5Validator(client=client)

    entry_price = 1.1000
    symbol = 'EURUSD'

    # Validate stop loss for BUY order
    print("\n1. Stop Loss Validation (BUY Order):")
    print(f"   Entry Price: {entry_price}")

    valid, msg = validator.validate(
        'stop_loss', 1.0900,
        entry_price=entry_price,
        order_type=OrderType.BUY,
        symbol=symbol
    )
    print(f"  SL 1.0900 (below entry): {'✓ Valid' if valid else '✗ Invalid'} - {msg}")

    valid, msg = validator.validate(
        'stop_loss', 1.1100,
        entry_price=entry_price,
        order_type=OrderType.BUY,
        symbol=symbol
    )
    print(f"  SL 1.1100 (above entry): {'✓ Valid' if valid else '✗ Invalid'} - {msg}")

    # Validate take profit for BUY order
    print("\n2. Take Profit Validation (BUY Order):")
    valid, msg = validator.validate(
        'take_profit', 1.1100,
        entry_price=entry_price,
        order_type=OrderType.BUY,
        symbol=symbol
    )
    print(f"  TP 1.1100 (above entry): {'✓ Valid' if valid else '✗ Invalid'} - {msg}")

    valid, msg = validator.validate(
        'take_profit', 1.0900,
        entry_price=entry_price,
        order_type=OrderType.BUY,
        symbol=symbol
    )
    print(f"  TP 1.0900 (below entry): {'✓ Valid' if valid else '✗ Invalid'} - {msg}")

    # Validate for SELL order
    print("\n3. Stop Loss/Take Profit Validation (SELL Order):")
    valid, msg = validator.validate(
        'stop_loss', 1.1100,
        entry_price=entry_price,
        order_type=OrderType.SELL,
        symbol=symbol
    )
    print(f"  SL 1.1100 (above entry): {'✓ Valid' if valid else '✗ Invalid'} - {msg}")

    valid, msg = validator.validate(
        'take_profit', 1.0900,
        entry_price=entry_price,
        order_type=OrderType.SELL,
        symbol=symbol
    )
    print(f"  TP 1.0900 (below entry): {'✓ Valid' if valid else '✗ Invalid'} - {msg}")

    client.disconnect()


def example3_order_type_validation():
    """Example 3: Order type validation."""
    print("\n" + "="*60)
    print("Example 3: Order Type Validation")
    print("="*60)

    validator = MT5Validator()

    print("\n1. String Order Types:")
    for order_type in ['BUY', 'SELL', 'BUY_LIMIT', 'SELL_STOP', 'INVALID']:
        valid, msg = validator.validate('order_type', order_type)
        print(f"  {order_type}: {'✓ Valid' if valid else '✗ Invalid'}")

    print("\n2. Integer Order Types:")
    for order_type in [0, 1, 2, 3, 999]:
        valid, msg = validator.validate('order_type', order_type)
        print(f"  {order_type}: {'✓ Valid' if valid else '✗ Invalid'}")


def example4_timeframe_validation():
    """Example 4: Timeframe validation."""
    print("\n" + "="*60)
    print("Example 4: Timeframe Validation")
    print("="*60)

    validator = MT5Validator()

    print("\n1. String Timeframes:")
    for tf in ['M1', 'M5', 'H1', 'D1', 'INVALID']:
        valid, msg = validator.validate('timeframe', tf)
        print(f"  {tf}: {'✓ Valid' if valid else '✗ Invalid'}")

    print("\n2. Enum Timeframes:")
    for tf in [TimeFrame.M1, TimeFrame.H1, TimeFrame.D1]:
        valid, msg = validator.validate('timeframe', tf)
        print(f"  {tf.name}: {'✓ Valid' if valid else '✗ Invalid'}")

    print("\n3. Integer Timeframes:")
    for tf in [1, 60, 1440, 999]:
        valid, msg = validator.validate('timeframe', tf)
        print(f"  {tf}: {'✓ Valid' if valid else '✗ Invalid'}")


def example5_date_range_validation():
    """Example 5: Date range validation."""
    print("\n" + "="*60)
    print("Example 5: Date Range Validation")
    print("="*60)

    validator = MT5Validator()

    print("\n1. Valid Date Ranges:")
    start = datetime.now() - timedelta(days=30)
    end = datetime.now() - timedelta(days=1)
    valid, msg = validator.validate('date_range', start, end_date=end)
    print(f"  Last 30 days: {'✓ Valid' if valid else '✗ Invalid'} - {msg}")

    print("\n2. Invalid Date Ranges:")
    # Start too far in past
    start = datetime.now() - timedelta(days=4000)
    valid, msg = validator.validate('date_range', start)
    print(f"  Start 4000 days ago: {'✓ Valid' if valid else '✗ Invalid'} - {msg}")

    # End before start
    start = datetime.now() - timedelta(days=1)
    end = datetime.now() - timedelta(days=30)
    valid, msg = validator.validate('date_range', start, end_date=end)
    print(f"  End before start: {'✓ Valid' if valid else '✗ Invalid'} - {msg}")

    # End in future
    start = datetime.now() - timedelta(days=30)
    end = datetime.now() + timedelta(days=1)
    valid, msg = validator.validate('date_range', start, end_date=end)
    print(f"  End in future: {'✓ Valid' if valid else '✗ Invalid'} - {msg}")


def example6_trade_request_validation():
    """Example 6: Complete trade request validation."""
    print("\n" + "="*60)
    print("Example 6: Trade Request Validation")
    print("="*60)

    creds = get_credentials_from_config()
    if not creds:
        print("✗ Failed to load credentials from config.ini")
        return

    client = MT5Client()
    client.initialize(login=creds['login'], password=creds['password'], server=creds['server'])

    validator = MT5Validator(client=client)

    # Valid trade request
    print("\n1. Valid Trade Request:")
    request = {
        'action': mt5.TRADE_ACTION_DEAL,
        'symbol': 'EURUSD',
        'volume': 0.1,
        'type': mt5.ORDER_TYPE_BUY,
        'price': 1.1000,
        'sl': 1.0900,
        'tp': 1.1100,
        'magic': 12345,
        'deviation': 10
    }
    valid, msg = validator.validate('trade_request', request)
    print(f"  Request: {'✓ Valid' if valid else '✗ Invalid'} - {msg}")

    # Invalid requests
    print("\n2. Invalid Trade Requests:")

    # Missing required field
    request = {
        'action': mt5.TRADE_ACTION_DEAL,
        'symbol': 'EURUSD',
        # Missing volume and type
    }
    valid, msg = validator.validate('trade_request', request)
    print(f"  Missing fields: {'✓ Valid' if valid else '✗ Invalid'} - {msg}")

    # Invalid volume
    request = {
        'action': mt5.TRADE_ACTION_DEAL,
        'symbol': 'EURUSD',
        'volume': -0.1,
        'type': mt5.ORDER_TYPE_BUY
    }
    valid, msg = validator.validate('trade_request', request)
    print(f"  Negative volume: {'✓ Valid' if valid else '✗ Invalid'} - {msg}")

    # Invalid stop loss
    request = {
        'action': mt5.TRADE_ACTION_DEAL,
        'symbol': 'EURUSD',
        'volume': 0.1,
        'type': mt5.ORDER_TYPE_BUY,
        'price': 1.1000,
        'sl': 1.1100,  # Above entry for BUY
    }
    valid, msg = validator.validate('trade_request', request)
    print(f"  Invalid SL: {'✓ Valid' if valid else '✗ Invalid'} - {msg}")

    client.disconnect()


def example7_credentials_validation():
    """Example 7: Credentials validation."""
    print("\n" + "="*60)
    print("Example 7: Credentials Validation")
    print("="*60)

    validator = MT5Validator()

    # Valid credentials
    print("\n1. Valid Credentials:")
    credentials = {
        'login': 12345678,
        'password': 'SecurePassword123',
        'server': 'MetaQuotes-Demo'
    }
    valid, msg = validator.validate('credentials', credentials)
    print(f"  {'✓ Valid' if valid else '✗ Invalid'} - {msg}")

    # Invalid credentials
    print("\n2. Invalid Credentials:")

    # Missing field
    credentials = {
        'login': 12345678,
        'password': 'SecurePassword123'
        # Missing server
    }
    valid, msg = validator.validate('credentials', credentials)
    print(f"  Missing server: {'✓ Valid' if valid else '✗ Invalid'} - {msg}")

    # Invalid login
    credentials = {
        'login': -12345,
        'password': 'SecurePassword123',
        'server': 'MetaQuotes-Demo'
    }
    valid, msg = validator.validate('credentials', credentials)
    print(f"  Negative login: {'✓ Valid' if valid else '✗ Invalid'} - {msg}")

    # Empty password
    credentials = {
        'login': 12345678,
        'password': '',
        'server': 'MetaQuotes-Demo'
    }
    valid, msg = validator.validate('credentials', credentials)
    print(f"  Empty password: {'✓ Valid' if valid else '✗ Invalid'} - {msg}")


def example8_batch_validation():
    """Example 8: Batch validation."""
    print("\n" + "="*60)
    print("Example 8: Batch Validation")
    print("="*60)

    creds = get_credentials_from_config()
    if not creds:
        print("✗ Failed to load credentials from config.ini")
        return

    client = MT5Client()
    client.initialize(login=creds['login'], password=creds['password'], server=creds['server'])

    validator = MT5Validator(client=client)

    # Validate multiple parameters
    print("\n1. All Valid Parameters:")
    validations = [
        {'type': 'symbol', 'value': 'EURUSD'},
        {'type': 'volume', 'value': 0.1, 'symbol': 'EURUSD'},
        {'type': 'price', 'value': 1.1000, 'symbol': 'EURUSD'},
        {'type': 'magic', 'value': 12345},
        {'type': 'deviation', 'value': 10}
    ]

    all_valid, errors = validator.validate_multiple(validations)
    print(f"  Result: {'✓ All Valid' if all_valid else '✗ Some Invalid'}")
    if errors:
        for error in errors:
            print(f"    - {error}")

    # Some invalid parameters
    print("\n2. Some Invalid Parameters:")
    validations = [
        {'type': 'symbol', 'value': 'EURUSD'},
        {'type': 'volume', 'value': -0.1},  # Invalid
        {'type': 'price', 'value': 1.1000},
        {'type': 'magic', 'value': -1},  # Invalid
    ]

    all_valid, errors = validator.validate_multiple(validations)
    print(f"  Result: {'✓ All Valid' if all_valid else '✗ Some Invalid'}")
    if errors:
        for error in errors:
            print(f"    - {error}")

    client.disconnect()


def example9_margin_validation():
    """Example 9: Margin validation."""
    print("\n" + "="*60)
    print("Example 9: Margin Validation")
    print("="*60)

    creds = get_credentials_from_config()
    if not creds:
        print("✗ Failed to load credentials from config.ini")
        return

    client = MT5Client()
    client.initialize(login=creds['login'], password=creds['password'], server=creds['server'])

    validator = MT5Validator(client=client)

    # Get account info to show free margin
    account_info = mt5.account_info()
    if account_info:
        print(f"\nAccount Free Margin: ${account_info.margin_free:.2f}")

        # Validate different margin requirements
        print("\n1. Margin Validation:")
        for margin in [100.0, 5000.0, account_info.margin_free * 0.5, account_info.margin_free * 1.5]:
            valid, msg = validator.validate('margin', margin)
            print(f"  ${margin:.2f}: {'✓ Valid' if valid else '✗ Invalid'} - {msg}")

    client.disconnect()


def example10_validation_rules_management():
    """Example 10: Managing validation rules."""
    print("\n" + "="*60)
    print("Example 10: Validation Rules Management")
    print("="*60)

    validator = MT5Validator()

    # Get current rules
    print("\n1. Current Validation Rules:")
    rules = validator.get_validation_rules()
    print(f"  Volume min: {rules['volume']['min']}")
    print(f"  Volume max: {rules['volume']['max']}")
    print(f"  Volume step: {rules['volume']['step']}")
    print(f"  Price min: {rules['price']['min']}")
    print(f"  Price max: {rules['price']['max']}")

    # Update a rule
    print("\n2. Updating Volume Minimum:")
    print(f"  Before: {rules['volume']['min']}")
    validator.update_validation_rule('volume', 'min', 0.001)
    updated_rules = validator.get_validation_rules()
    print(f"  After: {updated_rules['volume']['min']}")

    # Test with updated rule
    print("\n3. Testing with Updated Rule:")
    valid, msg = validator.validate('volume', 0.005)
    print(f"  0.005 lots: {'✓ Valid' if valid else '✗ Invalid'} - {msg}")


def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("MT5Validator Usage Examples")
    print("="*60)

    try:
        # Run basic examples
        example1_basic_validation()
        example2_stop_loss_take_profit()
        example3_order_type_validation()
        example4_timeframe_validation()
        example5_date_range_validation()
        example6_trade_request_validation()
        example7_credentials_validation()
        example8_batch_validation()
        example9_margin_validation()
        example10_validation_rules_management()

        print("\n" + "="*60)
        print("Examples completed!")
        print("="*60)

    except KeyboardInterrupt:
        print("\n\nExamples cancelled by user")
    except Exception as e:
        logger.error(f"Error running examples: {e}")
        print(f"\nError: {e}")


if __name__ == "__main__":
    main()
