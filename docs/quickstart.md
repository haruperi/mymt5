# MyMT5 Quick Start Guide

Welcome to MyMT5! This guide will help you get started with the MetaTrader 5 Python trading system in minutes.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Basic Configuration](#basic-configuration)
4. [Your First Connection](#your-first-connection)
5. [Common Operations](#common-operations)
6. [Next Steps](#next-steps)

---

## Prerequisites

Before you begin, ensure you have:

- **Python 3.8 or higher** installed
- **MetaTrader 5 terminal** installed on your system
- **A demo or live MT5 account** with credentials (login, password, server)
- **Basic Python knowledge** (variables, functions, classes)

### Check Your Python Version

```bash
python --version
# Should show Python 3.8 or higher
```

### Verify MT5 Installation

Make sure MetaTrader 5 is installed. Default locations:
- **Windows**: `C:\Program Files\MetaTrader 5\terminal64.exe`
- Check your Start Menu for "MetaTrader 5"

---

## Installation

### Step 1: Create a Project Directory

```bash
mkdir my_mt5_project
cd my_mt5_project
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate

# On Linux/Mac:
source venv/bin/activate
```

### Step 3: Install MyMT5

```bash
# If installing from local directory
pip install -e path/to/mymt5

# Or if you have the package
pip install mymt5

# Install dependencies
pip install MetaTrader5 pandas numpy python-dateutil
```

### Verify Installation

```python
# Test import
python -c "from mymt5 import MT5Client; print('Success!')"
```

---

## Basic Configuration

### Option 1: Configuration File (Recommended)

Create a `config.ini` file in your project directory:

```ini
[MT5]
login=YOUR_ACCOUNT_NUMBER
password=YOUR_PASSWORD
server=YOUR_BROKER_SERVER
path=C:\Program Files\MetaTrader 5\terminal64.exe
timeout=60000
```

**Important**: Add `config.ini` to your `.gitignore` to keep credentials secure!

### Option 2: Environment Variables

```bash
# Windows PowerShell
$env:MT5_LOGIN="12345678"
$env:MT5_PASSWORD="YourPassword"
$env:MT5_SERVER="YourBroker-Demo"

# Linux/Mac
export MT5_LOGIN="12345678"
export MT5_PASSWORD="YourPassword"
export MT5_SERVER="YourBroker-Demo"
```

### Option 3: Direct Credentials (For Testing Only)

```python
credentials = {
    'login': 12345678,
    'password': 'YourPassword',
    'server': 'YourBroker-Demo'
}
```

---

## Your First Connection

### Example 1: Simple Connection

```python
from mymt5 import MT5Client

# Create client
client = MT5Client()

# Initialize with credentials
success = client.initialize(
    login=12345678,
    password='YourPassword',
    server='YourBroker-Demo'
)

if success:
    print("Connected successfully!")
    print(f"Connection state: {client.get_status()}")
else:
    print("Connection failed!")
    error = client.get_error()
    print(f"Error: {error}")

# Always cleanup
client.shutdown()
```

### Example 2: Connection with Config File

```python
from mymt5 import MT5Client
import configparser

# Load configuration
config = configparser.ConfigParser()
config.read('config.ini')

# Create and initialize client
client = MT5Client(
    path=config['MT5'].get('path'),
    timeout=int(config['MT5'].get('timeout', 60000))
)

client.initialize(
    login=int(config['MT5']['login']),
    password=config['MT5']['password'],
    server=config['MT5']['server']
)

if client.is_connected():
    print("✓ Connected!")
    
client.shutdown()
```

### Example 3: Using Context Manager (Best Practice)

```python
from mymt5 import MT5Client
from contextlib import contextmanager

@contextmanager
def mt5_connection(**credentials):
    """Context manager for safe MT5 connection"""
    client = MT5Client()
    try:
        client.initialize(**credentials)
        yield client
    finally:
        client.shutdown()

# Usage
with mt5_connection(login=12345678, password='pass', server='server') as client:
    if client.is_connected():
        print("Connected!")
        # Do your trading operations here
```

---

## Common Operations

### Get Account Information

```python
from mymt5 import MT5Client, MT5Account

client = MT5Client()
client.initialize(login=12345678, password='pass', server='server')

# Create account manager
account = MT5Account(client)

# Get balance
balance = account.get('balance')
print(f"Balance: ${balance}")

# Get equity
equity = account.get('equity')
print(f"Equity: ${equity}")

# Get all account info
info = account.get()
print(f"Account Info: {info}")

# Check account status
is_demo = account.check('demo')
print(f"Is Demo Account: {is_demo}")

client.shutdown()
```

### Get Symbol Information

```python
from mymt5 import MT5Client, MT5Symbol

client = MT5Client()
client.initialize(login=12345678, password='pass', server='server')

# Create symbol manager
symbol = MT5Symbol(client)

# Get current price
price = symbol.get_price('EURUSD', 'bid')
print(f"EUR/USD Bid: {price}")

# Get symbol information
info = symbol.get_info('EURUSD')
print(f"Point: {info['point']}")
print(f"Digits: {info['digits']}")
print(f"Spread: {info['spread']}")

# Check if symbol is available
is_available = symbol.check('EURUSD', 'available')
print(f"EURUSD Available: {is_available}")

client.shutdown()
```

### Get Market Data

```python
from mymt5 import MT5Client, MT5Data
from datetime import datetime, timedelta

client = MT5Client()
client.initialize(login=12345678, password='pass', server='server')

# Create data manager
data = MT5Data(client)

# Get last 100 bars
bars = data.get_bars(
    symbol='EURUSD',
    timeframe='H1',
    count=100
)
print(f"Retrieved {len(bars)} bars")
print(bars.head())

# Get bars for specific date range
end_date = datetime.now()
start_date = end_date - timedelta(days=7)

bars = data.get_bars(
    symbol='EURUSD',
    timeframe='H1',
    start_date=start_date,
    end_date=end_date
)
print(f"Retrieved {len(bars)} bars for last 7 days")

client.shutdown()
```

### Execute a Simple Trade

```python
from mymt5 import MT5Client, MT5Trade, MT5Symbol

client = MT5Client()
client.initialize(login=12345678, password='pass', server='server')

# Create trade and symbol managers
trade = MT5Trade(client, symbol_manager=MT5Symbol(client))

# Execute buy order
result = trade.buy(
    symbol='EURUSD',
    volume=0.01,  # 0.01 lot = 1000 units
    stop_loss=1.0900,  # Your SL price
    take_profit=1.1100,  # Your TP price
    comment='My first trade',
    magic=12345
)

if result['success']:
    print(f"✓ Trade opened successfully!")
    print(f"Order ticket: {result['order']}")
    print(f"Volume: {result['volume']}")
    print(f"Price: {result['price']}")
else:
    print(f"✗ Trade failed: {result['error']}")

client.shutdown()
```

### Close a Position

```python
from mymt5 import MT5Client, MT5Trade, MT5Symbol

client = MT5Client()
client.initialize(login=12345678, password='pass', server='server')

trade = MT5Trade(client, symbol_manager=MT5Symbol(client))

# Get all positions
positions = trade.get_positions()
print(f"Open positions: {len(positions)}")

# Close specific position by ticket
if positions:
    ticket = positions[0]['ticket']
    result = trade.close_position(ticket=ticket)
    
    if result['success']:
        print(f"✓ Position {ticket} closed")
    else:
        print(f"✗ Failed to close: {result['error']}")

# Close all positions for a symbol
result = trade.close_position(symbol='EURUSD')
print(f"Closed positions: {result}")

client.shutdown()
```

### Calculate Position Size with Risk Management

```python
from mymt5 import MT5Client, MT5Risk, MT5Account

client = MT5Client()
client.initialize(login=12345678, password='pass', server='server')

# Create risk and account managers
risk = MT5Risk(client, account_manager=MT5Account(client))

# Calculate position size (risk 1% of account)
size = risk.calculate_size(
    symbol='EURUSD',
    method='percent',  # Risk 1% of account
    risk_percent=1.0,
    entry_price=1.1000,
    stop_loss=1.0950  # 50 pips stop loss
)

print(f"Recommended position size: {size['volume']} lots")
print(f"Risk amount: ${size['risk_amount']}")
print(f"Risk percent: {size['risk_percent']}%")

client.shutdown()
```

---

## Next Steps

Congratulations! You now know the basics of MyMT5. Here's what to explore next:

### 1. Explore Examples

Check out the `examples/` directory for comprehensive examples:

```bash
# Basic examples
python examples/01_basic_connection.py
python examples/02_account_info.py
python examples/03_market_data.py

# Trading examples
python examples/04_simple_trade.py
python examples/05_risk_management.py
python examples/07_trading_operations.py

# Advanced examples
python examples/08_validation.py
python examples/09_strategy_template.py
python examples/10_advanced_trading.py
```

### 2. Read Documentation

- **[User Guide](user_guide.md)**: Comprehensive guide to all features
- **[API Reference](api_reference.md)**: Complete API documentation
- **[Configuration Guide](configuration.md)**: Advanced configuration options
- **[Troubleshooting](troubleshooting.md)**: Common issues and solutions

### 3. Learn Advanced Features

- **Auto-reconnection**: Automatic connection recovery
- **Multi-account support**: Switch between multiple accounts
- **Event system**: Subscribe to connection events
- **Data caching**: Improve performance with caching
- **Streaming data**: Real-time data streaming
- **Batch operations**: Execute multiple trades efficiently

### 4. Build Your Strategy

1. Start with the strategy template: `examples/09_strategy_template.py`
2. Implement your trading logic
3. Add risk management rules
4. Test with a demo account
5. Monitor and optimize

---

## Quick Reference

### Essential Imports

```python
from mymt5 import (
    MT5Client,      # Connection management
    MT5Account,     # Account information
    MT5Symbol,      # Symbol operations
    MT5Data,        # Market data
    MT5Trade,       # Trading operations
    MT5Risk,        # Risk management
    MT5History,     # Historical data
    MT5Validator,   # Validation
    MT5Utils,       # Utility functions
)
```

### Basic Workflow

```python
# 1. Initialize
client = MT5Client()
client.initialize(login=..., password=..., server=...)

# 2. Create managers
account = MT5Account(client)
symbol = MT5Symbol(client)
trade = MT5Trade(client, symbol_manager=symbol)

# 3. Do operations
# ... your trading logic ...

# 4. Cleanup
client.shutdown()
```

### Common Methods

```python
# Client
client.is_connected()
client.get_status()
client.reconnect()

# Account
account.get('balance')
account.get('equity')
account.check('demo')

# Symbol
symbol.get_price('EURUSD', 'bid')
symbol.get_info('EURUSD')
symbol.check('EURUSD', 'tradable')

# Trade
trade.buy(symbol, volume, ...)
trade.sell(symbol, volume, ...)
trade.get_positions()
trade.close_position(ticket)

# Data
data.get_bars(symbol, timeframe, count)
data.get_ticks(symbol, count)
```

---

## Troubleshooting Quick Tips

### "Module not found" Error
```bash
pip install -e path/to/mymt5
```

### Connection Failed
- Verify MT5 is installed
- Check credentials (login, password, server)
- Ensure MT5 terminal is not already running
- Check firewall settings

### "Symbol not found"
```python
# Initialize symbol first
symbol.initialize('EURUSD')
```

### Import Errors
```bash
pip install MetaTrader5 pandas numpy
```

---

## Need Help?

- 📖 Read the [User Guide](user_guide.md)
- 🔍 Check [Troubleshooting](troubleshooting.md)
- 💡 Review [examples/](../examples/)
- 📚 Browse [API Reference](api_reference.md)

---

**Ready to trade?** Start with `examples/01_basic_connection.py` and work your way up!

Happy Trading! 📈💰

