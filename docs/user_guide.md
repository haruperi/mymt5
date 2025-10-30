# MyMT5 User Guide

Complete guide to using the MyMT5 MetaTrader 5 Python trading system.

## Table of Contents

1. [Introduction](#introduction)
2. [Architecture Overview](#architecture-overview)
3. [Core Components](#core-components)
4. [Connection Management](#connection-management)
5. [Account Operations](#account-operations)
6. [Symbol Management](#symbol-management)
7. [Market Data](#market-data)
8. [Trading Operations](#trading-operations)
9. [Risk Management](#risk-management)
10. [Historical Analysis](#historical-analysis)
11. [Validation](#validation)
12. [Utilities](#utilities)
13. [Best Practices](#best-practices)
14. [Advanced Topics](#advanced-topics)

---

## Introduction

MyMT5 is a comprehensive Python library for interacting with MetaTrader 5 terminal. It provides a clean, Pythonic interface for trading operations, market data retrieval, risk management, and historical analysis.

### Key Features

- ✅ **Connection Management**: Robust connection handling with auto-reconnection
- ✅ **Multi-Account Support**: Seamlessly switch between multiple accounts
- ✅ **Complete Trading API**: Market orders, pending orders, position management
- ✅ **Risk Management**: Position sizing, risk calculations, portfolio analytics
- ✅ **Market Data**: Real-time quotes, historical bars, tick data
- ✅ **Historical Analysis**: Performance metrics, trade analysis, reporting
- ✅ **Input Validation**: Comprehensive parameter validation
- ✅ **Event System**: Subscribe to connection and trading events

---

## Architecture Overview

MyMT5 is organized into 5 layers:

```
┌─────────────────────────────────┐
│      Core Layer                 │
│      (MT5Client)                │
└─────────────────────────────────┘
           ↓
┌─────────────────────────────────┐
│   Information Layer             │
│   Account │ Symbol │ Terminal   │
└─────────────────────────────────┘
           ↓
┌─────────────────────────────────┐
│      Data Layer                 │
│      Data │ History             │
└─────────────────────────────────┘
           ↓
┌─────────────────────────────────┐
│    Trading Layer                │
│      Trade │ Risk               │
└─────────────────────────────────┘
           ↓
┌─────────────────────────────────┐
│    Utility Layer                │
│   Validator │ Utils             │
└─────────────────────────────────┘
```

---

## Core Components

### MT5Client

The core client manages the connection to MT5 terminal.

```python
from mymt5 import MT5Client

# Create client
client = MT5Client(
    path='C:/Program Files/MetaTrader 5/terminal64.exe',
    timeout=60000,
    portable=False
)

# Initialize connection
client.initialize(
    login=12345678,
    password='YourPassword',
    server='YourBroker-Demo'
)

# Check connection
if client.is_connected():
    print("Connected!")

# Cleanup
client.shutdown()
```

### Component Managers

All other components require a client instance:

```python
from mymt5 import MT5Account, MT5Symbol, MT5Data, MT5Trade

# Create managers
account = MT5Account(client)
symbol = MT5Symbol(client)
data = MT5Data(client)
trade = MT5Trade(client, symbol_manager=symbol)
```

---

## Connection Management

### Basic Connection

```python
client = MT5Client()

# Method 1: initialize() - connect and login
client.initialize(login=12345, password='pass', server='server')

# Method 2: connect() then login()
client.connect()
client.login(login=12345, password='pass', server='server')
```

### Auto-Reconnection

Enable automatic reconnection on connection loss:

```python
# Enable auto-reconnection
client.enable_auto_reconnect()

# Configure retry behavior
client.set_retry_attempts(5)  # Try 5 times
client.set_retry_delay(3)     # Wait 3 seconds between attempts

# Disable auto-reconnection
client.disable_auto_reconnect()

# Manual reconnection
success = client.reconnect()
```

### Multi-Account Support

Switch between multiple accounts:

```python
# Save current account configuration
client.save_account('demo_account_1')

# Add another account
client.switch_account(
    account_name='live_account_1',
    login=87654321,
    password='LivePass',
    server='YourBroker-Live'
)

# List all saved accounts
accounts = client.list_accounts()
print(accounts)  # ['demo_account_1', 'live_account_1']

# Switch back to demo
client.switch_account('demo_account_1')

# Remove account
client.remove_account('demo_account_1')
```

### Event System

Subscribe to connection events:

```python
def on_connect(client):
    print(f"Connected to {client.account_server}")

def on_disconnect(client):
    print("Disconnected from MT5")

def on_reconnect(client, attempt):
    print(f"Reconnection attempt {attempt}")

# Register event handlers
client.on('connect', on_connect)
client.on('disconnect', on_disconnect)
client.on('reconnect', on_reconnect)

# Unregister handler
client.off('connect', on_connect)
```

### Connection Status

```python
# Check connection state
is_connected = client.is_connected()
state = client.connection_state  # ConnectionState enum

# Get detailed status
status = client.get_status()
print(status)
# {
#     'connected': True,
#     'state': 'connected',
#     'login': 12345678,
#     'server': 'YourBroker-Demo',
#     'uptime': 3600,
#     ...
# }

# Get statistics
stats = client.get_connection_statistics()
print(stats)
# {
#     'connection_attempts': 1,
#     'successful_connections': 1,
#     'failed_connections': 0,
#     'reconnections': 0,
#     'total_uptime': 3600,
#     'last_error': None
# }

# Test connection
ping_result = client.ping()
```

---

## Account Operations

### Get Account Information

```python
account = MT5Account(client)

# Get specific attribute
balance = account.get('balance')
equity = account.get('equity')
margin = account.get('margin')
margin_free = account.get('margin_free')
profit = account.get('profit')

# Get all account info
info = account.get()
print(info)
# {
#     'login': 12345678,
#     'balance': 10000.0,
#     'equity': 10500.0,
#     'profit': 500.0,
#     'margin': 1000.0,
#     'margin_free': 9000.0,
#     'margin_level': 1050.0,
#     'leverage': 100,
#     'currency': 'USD',
#     'name': 'John Doe',
#     'server': 'YourBroker-Demo',
#     'company': 'Your Broker Ltd',
#     ...
# }
```

### Check Account Status

```python
# Check if demo account
is_demo = account.check('demo')

# Check if trading is allowed
trade_allowed = account.check('trade_allowed')

# Check if account is authorized
is_authorized = account.check('authorized')

# Check if expert advisors are allowed
expert_allowed = account.check('expert_allowed')
```

### Calculate Account Metrics

```python
# Calculate margin level
margin_level = account.calculate('margin_level')

# Calculate drawdown
drawdown = account.calculate('drawdown')
# {
#     'current_drawdown': 500.0,
#     'current_drawdown_percent': 5.0,
#     'max_drawdown': 1000.0,
#     'max_drawdown_percent': 10.0
# }

# Calculate health metrics
health = account.calculate('health')
# {
#     'margin_level': 1050.0,
#     'margin_usage_percent': 10.0,
#     'equity_to_balance_ratio': 1.05,
#     'profit_to_balance_ratio': 0.05,
#     'status': 'healthy'
# }

# Calculate required margin for trade
margin_required = account.calculate('margin_required', 
    symbol='EURUSD', 
    volume=1.0
)
```

### Account Summary and Export

```python
# Get summary
summary = account.get_summary()
print(summary)

# Export account data
account.export('account_data.json', format='json')
account.export('account_data.csv', format='csv')
```

---

## Symbol Management

### Discover Symbols

```python
symbol_manager = MT5Symbol(client)

# Get all available symbols
all_symbols = symbol_manager.get_symbols('all')

# Get symbols in Market Watch
market_watch = symbol_manager.get_symbols('market_watch')

# Get symbols by group
forex_symbols = symbol_manager.get_symbols('group', pattern='Forex*')
metals = symbol_manager.get_symbols('group', pattern='*GOLD*')

# Search for specific symbols
eur_symbols = symbol_manager.get_symbols('search', query='EUR')
```

### Market Watch Management

```python
# Initialize symbol (add to Market Watch if not present)
symbol_manager.initialize('EURUSD')

# Add symbol to Market Watch
symbol_manager.manage('add', 'GBPUSD')

# Remove symbol from Market Watch
symbol_manager.manage('remove', 'GBPUSD')

# Select symbol (make it active)
symbol_manager.manage('select', 'EURUSD')
```

### Get Symbol Information

```python
# Get specific attribute
point = symbol_manager.get_info('EURUSD', 'point')
digits = symbol_manager.get_info('EURUSD', 'digits')
spread = symbol_manager.get_info('EURUSD', 'spread')
tick_size = symbol_manager.get_info('EURUSD', 'trade_tick_size')
lot_min = symbol_manager.get_info('EURUSD', 'volume_min')
lot_max = symbol_manager.get_info('EURUSD', 'volume_max')
lot_step = symbol_manager.get_info('EURUSD', 'volume_step')

# Get all symbol information
info = symbol_manager.get_info('EURUSD')
print(info)
```

### Real-Time Prices

```python
# Get current price
current = symbol_manager.get_price('EURUSD', 'current')

# Get bid/ask
bid = symbol_manager.get_price('EURUSD', 'bid')
ask = symbol_manager.get_price('EURUSD', 'ask')
spread = ask - bid

# Get last traded price
last = symbol_manager.get_price('EURUSD', 'last')

# Get all prices
prices = symbol_manager.get_price('EURUSD')
# {
#     'bid': 1.10000,
#     'ask': 1.10005,
#     'last': 1.10002,
#     'time': datetime(...),
#     'volume': 100
# }
```

### Symbol Status Checks

```python
# Check if symbol exists
exists = symbol_manager.check('EURUSD', 'exists')

# Check if symbol is visible in Market Watch
visible = symbol_manager.check('EURUSD', 'visible')

# Check if symbol is tradable
tradable = symbol_manager.check('EURUSD', 'tradable')

# Check if market is open
market_open = symbol_manager.check('EURUSD', 'market_open')
```

### Validate Symbol and Volume

```python
# Validate symbol exists and is tradable
valid, error = symbol_manager.validate('EURUSD', 'exists')
valid, error = symbol_manager.validate('EURUSD', 'tradable')

# Validate volume
valid, error = symbol_manager.validate_volume('EURUSD', 1.5)
if not valid:
    print(f"Invalid volume: {error}")
```

---

## Market Data

### Get OHLCV Data (Bars/Candles)

```python
data_manager = MT5Data(client)

# Get last N bars
bars = data_manager.get_bars(
    symbol='EURUSD',
    timeframe='H1',
    count=100
)
print(bars.head())

# Get bars by date range
from datetime import datetime, timedelta

end_date = datetime.now()
start_date = end_date - timedelta(days=30)

bars = data_manager.get_bars(
    symbol='EURUSD',
    timeframe='D1',
    start_date=start_date,
    end_date=end_date
)

# Return as dict instead of DataFrame
bars = data_manager.get_bars(
    symbol='EURUSD',
    timeframe='M15',
    count=50,
    as_dataframe=False
)
```

### Get Tick Data

```python
# Get last N ticks
ticks = data_manager.get_ticks(
    symbol='EURUSD',
    count=1000
)

# Get ticks by date range
ticks = data_manager.get_ticks(
    symbol='EURUSD',
    start_date=start_date,
    end_date=end_date,
    flags='all'  # 'all', 'trade', 'bid', 'ask'
)
```

### Stream Real-Time Data

```python
def on_tick(tick):
    print(f"Tick: {tick['symbol']} - {tick['bid']}/{tick['ask']}")

def on_bar(bar):
    print(f"New bar: {bar['time']} - O:{bar['open']} H:{bar['high']} L:{bar['low']} C:{bar['close']}")

# Stream ticks
data_manager.stream(
    'ticks',
    symbol='EURUSD',
    callback=on_tick,
    interval=1  # seconds
)

# Stream bars
data_manager.stream(
    'bars',
    symbol='EURUSD',
    timeframe='M1',
    callback=on_bar,
    interval=60  # seconds
)

# Stop streaming
data_manager.stop_stream()
```

### Data Processing

```python
# Normalize data (scale to 0-1)
normalized = data_manager.process('normalize', bars)

# Clean data (remove outliers)
cleaned = data_manager.process('clean', bars, std_threshold=3)

# Fill missing data
filled = data_manager.process('fill_missing', bars, method='forward')

# Detect gaps
gaps = data_manager.process('detect_gaps', bars)

# Resample to different timeframe
resampled = data_manager.process('resample', bars, target_timeframe='H4')
```

### Data Caching

```python
# Cache data
data_manager.cache(
    key='eurusd_h1_100',
    data=bars,
    ttl=3600  # Cache for 1 hour
)

# Get cached data
cached = data_manager.get_cached('eurusd_h1_100')

# Clear cache
data_manager.clear_cache()  # Clear all
data_manager.clear_cache('eurusd_h1_100')  # Clear specific
```

### Export Data

```python
# Export to CSV
data_manager.export(bars, 'eurusd_h1.csv', format='csv')

# Export to JSON
data_manager.export(bars, 'eurusd_h1.json', format='json')

# Export to Parquet
data_manager.export(bars, 'eurusd_h1.parquet', format='parquet')

# Export to database
data_manager.export(bars, 'eurusd_h1', format='database', 
    connection_string='sqlite:///data.db')
```

---

## Trading Operations

### Execute Market Orders

```python
trade_manager = MT5Trade(client, symbol_manager=MT5Symbol(client))

# Buy order
result = trade_manager.buy(
    symbol='EURUSD',
    volume=0.01,
    stop_loss=1.0950,
    take_profit=1.1050,
    comment='Buy EUR/USD',
    magic=12345,
    deviation=20
)

if result['success']:
    print(f"Order ticket: {result['order']}")
    print(f"Execution price: {result['price']}")
else:
    print(f"Error: {result['error']}")

# Sell order
result = trade_manager.sell(
    symbol='EURUSD',
    volume=0.01,
    stop_loss=1.1050,
    take_profit=1.0950,
    comment='Sell EUR/USD',
    magic=12345
)
```

### Execute Pending Orders

```python
from mymt5.enums import OrderType

# Buy limit order
result = trade_manager.execute(
    symbol='EURUSD',
    order_type=OrderType.BUY_LIMIT,
    volume=0.01,
    price=1.0950,  # Buy at 1.0950
    stop_loss=1.0900,
    take_profit=1.1000,
    comment='Buy limit EUR/USD'
)

# Sell stop order
result = trade_manager.execute(
    symbol='EURUSD',
    order_type=OrderType.SELL_STOP,
    volume=0.01,
    price=1.0950,  # Sell if price drops to 1.0950
    stop_loss=1.1000,
    take_profit=1.0900
)

# Stop limit order
result = trade_manager.execute(
    symbol='EURUSD',
    order_type=OrderType.BUY_STOP_LIMIT,
    volume=0.01,
    price=1.1000,  # Stop price
    stoplimit=1.1005,  # Limit price
    stop_loss=1.0950,
    take_profit=1.1050
)
```

### Position Management

```python
# Get all positions
positions = trade_manager.get_positions()

# Get positions for specific symbol
eurusd_positions = trade_manager.get_positions(symbol='EURUSD')

# Get specific position by ticket
position = trade_manager.get_positions(ticket=123456)

# Close position fully
result = trade_manager.close_position(ticket=123456)

# Close position partially
result = trade_manager.close_position(ticket=123456, volume=0.01)

# Close all positions for a symbol
result = trade_manager.close_position(symbol='EURUSD')

# Close all positions
result = trade_manager.close_position()

# Reverse position (close and open opposite)
result = trade_manager.reverse_position(ticket=123456)
```

### Order Management

```python
# Get all pending orders
orders = trade_manager.get_orders()

# Get orders for specific symbol
eurusd_orders = trade_manager.get_orders(symbol='EURUSD')

# Get specific order by ticket
order = trade_manager.get_orders(ticket=123456)

# Modify order
result = trade_manager.modify_order(
    ticket=123456,
    price=1.0960,  # New price
    stop_loss=1.0910,  # New SL
    take_profit=1.1010  # New TP
)

# Cancel order
result = trade_manager.cancel_order(ticket=123456)

# Cancel all orders for symbol
result = trade_manager.cancel_order(symbol='EURUSD')

# Cancel all orders
result = trade_manager.cancel_order()
```

### Modify Positions

```python
# Modify stop loss and take profit
result = trade_manager.modify_position(
    ticket=123456,
    stop_loss=1.0960,
    take_profit=1.1040
)

# Remove stop loss
result = trade_manager.modify_position(ticket=123456, stop_loss=0)

# Remove take profit
result = trade_manager.modify_position(ticket=123456, take_profit=0)
```

### Position Analytics

```python
# Analyze position profit
profit = trade_manager.analyze_position(ticket=123456, metric='profit')
profit_points = trade_manager.analyze_position(ticket=123456, metric='profit_points')

# Get position duration
duration = trade_manager.analyze_position(ticket=123456, metric='duration')

# Get all position analytics
analytics = trade_manager.analyze_position(ticket=123456, metric='all')
# {
#     'profit': 50.0,
#     'profit_points': 50,
#     'profit_percent': 5.0,
#     'duration': timedelta(hours=2),
#     'current_price': 1.1005,
#     'entry_price': 1.1000,
#     'volume': 0.01
# }

# Get statistics for all positions
stats = trade_manager.get_position_stats()
# {
#     'total_positions': 5,
#     'total_volume': 0.15,
#     'total_profit': 250.0,
#     'winning_positions': 3,
#     'losing_positions': 2,
#     'largest_profit': 100.0,
#     'largest_loss': -50.0
# }
```

---

## Risk Management

### Position Sizing

```python
risk_manager = MT5Risk(client, account_manager=MT5Account(client))

# Calculate position size based on risk percentage
size = risk_manager.calculate_size(
    symbol='EURUSD',
    method='percent',
    risk_percent=1.0,  # Risk 1% of account
    entry_price=1.1000,
    stop_loss=1.0950  # 50 pips SL
)
print(f"Position size: {size['volume']} lots")
print(f"Risk amount: ${size['risk_amount']}")

# Calculate size based on fixed amount
size = risk_manager.calculate_size(
    symbol='EURUSD',
    method='amount',
    risk_amount=100.0,  # Risk $100
    entry_price=1.1000,
    stop_loss=1.0950
)

# Calculate size based on reward/risk ratio
size = risk_manager.calculate_size(
    symbol='EURUSD',
    method='ratio',
    risk_percent=1.0,
    reward_ratio=2.0,  # Target 2:1 reward/risk
    entry_price=1.1000,
    stop_loss=1.0950
)
```

### Risk Calculation

```python
# Calculate risk amount for a trade
risk = risk_manager.calculate_risk(
    symbol='EURUSD',
    volume=0.01,
    entry_price=1.1000,
    stop_loss=1.0950,
    metric='amount'
)
print(f"Risk: ${risk}")

# Calculate risk as percentage of account
risk_pct = risk_manager.calculate_risk(
    symbol='EURUSD',
    volume=0.01,
    entry_price=1.1000,
    stop_loss=1.0950,
    metric='percent'
)
print(f"Risk: {risk_pct}%")

# Calculate reward/risk ratio
ratio = risk_manager.calculate_risk(
    symbol='EURUSD',
    volume=0.01,
    entry_price=1.1000,
    stop_loss=1.0950,
    take_profit=1.1100,
    metric='reward_ratio'
)
print(f"Reward/Risk: {ratio}:1")

# Calculate all risk metrics
all_metrics = risk_manager.calculate_risk(
    symbol='EURUSD',
    volume=0.01,
    entry_price=1.1000,
    stop_loss=1.0950,
    take_profit=1.1100,
    metric='all'
)
```

### Set Risk Limits

```python
# Set maximum risk per trade (%)
risk_manager.set_limit('max_risk_per_trade', 2.0)

# Set maximum daily loss ($)
risk_manager.set_limit('max_daily_loss', 500.0)

# Set maximum number of positions
risk_manager.set_limit('max_positions', 5)

# Set maximum positions per symbol
risk_manager.set_limit('max_symbol_positions', 2)

# Set maximum total exposure (%)
risk_manager.set_limit('max_total_exposure', 20.0)

# Get current limit
max_risk = risk_manager.get_limit('max_risk_per_trade')
```

### Validate Risk

```python
# Validate if trade respects risk limits
violations = risk_manager.validate(
    symbol='EURUSD',
    volume=0.01,
    entry_price=1.1000,
    stop_loss=1.0950
)

if violations:
    print("Risk violations:")
    for violation in violations:
        print(f"- {violation}")
else:
    print("Trade is within risk limits")
```

### Portfolio Risk Analysis

```python
# Get total exposure
exposure = risk_manager.get_portfolio_risk('total_exposure')

# Get total risk
total_risk = risk_manager.get_portfolio_risk('total_risk')

# Get margin usage
margin_usage = risk_manager.get_portfolio_risk('margin_usage')

# Get correlation risk
correlation = risk_manager.get_portfolio_risk('correlation_risk')

# Get all portfolio risk metrics
all_risk = risk_manager.get_portfolio_risk('all')
# {
#     'total_exposure': 15.5,  # % of account
#     'total_risk': 3.5,  # % of account
#     'margin_usage': 25.0,  # % of available margin
#     'correlation_risk': 0.65,  # Correlation coefficient
#     'position_count': 5,
#     'symbols': ['EURUSD', 'GBPUSD', 'USDJPY']
# }
```

---

## Historical Analysis

### Retrieve Trade History

```python
history_manager = MT5History(client)

# Get deals (executed trades)
deals = history_manager.get('deals', days=30)

# Get orders (all orders including pending)
orders = history_manager.get('orders', days=30)

# Get both deals and orders
all_history = history_manager.get('both', days=7)

# Get history for specific date range
from datetime import datetime, timedelta

start = datetime.now() - timedelta(days=30)
end = datetime.now()

deals = history_manager.get('deals', start_date=start, end_date=end)

# Filter by symbol
eurusd_deals = history_manager.get('deals', days=30, symbol='EURUSD')
```

### Quick Access Methods

```python
# Get today's trades
today = history_manager.get_today()

# Get this week's trades
week = history_manager.get_period('week')

# Get this month's trades
month = history_manager.get_period('month')

# Get this year's trades
year = history_manager.get_period('year')
```

### Performance Metrics

```python
# Calculate win rate
win_rate = history_manager.calculate('win_rate', days=30)
print(f"Win rate: {win_rate}%")

# Calculate profit factor
profit_factor = history_manager.calculate('profit_factor', days=30)
print(f"Profit factor: {profit_factor}")

# Calculate average win/loss
avg_win = history_manager.calculate('avg_win', days=30)
avg_loss = history_manager.calculate('avg_loss', days=30)

# Calculate largest win/loss
largest_win = history_manager.calculate('largest_win', days=30)
largest_loss = history_manager.calculate('largest_loss', days=30)

# Calculate Sharpe ratio
sharpe = history_manager.calculate('sharpe_ratio', days=30)

# Calculate maximum drawdown
max_dd = history_manager.calculate('max_drawdown', days=30)

# Calculate totals
total_trades = history_manager.calculate('total_trades', days=30)
total_profit = history_manager.calculate('total_profit', days=30)
total_commission = history_manager.calculate('total_commission', days=30)
total_swap = history_manager.calculate('total_swap', days=30)
```

### Trade Analysis

```python
# Analyze trades by symbol
by_symbol = history_manager.analyze('by_symbol', days=30)

# Analyze by hour of day
by_hour = history_manager.analyze('by_hour', days=30)

# Analyze by day of week
by_weekday = history_manager.analyze('by_weekday', days=30)

# Analyze by month
by_month = history_manager.analyze('by_month', days=365)

# Get winning trades
winners = history_manager.analyze('winning_trades', days=30)

# Get losing trades
losers = history_manager.analyze('losing_trades', days=30)

# Get comprehensive statistics
stats = history_manager.analyze('statistics', days=30)
```

### Generate Reports

```python
# Performance report
performance = history_manager.generate_report('performance', days=30)

# Trade log report
trade_log = history_manager.generate_report('trade_log', days=7)

# Summary report
summary = history_manager.generate_report('summary', days=30)

# Detailed report (includes all metrics)
detailed = history_manager.generate_report('detailed', days=30)

# Export report to HTML
html_report = history_manager.generate_report(
    'detailed',
    days=30,
    format='html'
)

# Print report to console
history_manager.print_report('performance', days=30)
```

---

## Validation

### Validate Trading Parameters

```python
validator = MT5Validator(client)

# Validate symbol
valid, error = validator.validate('symbol', 'EURUSD')

# Validate volume
valid, error = validator.validate('volume', symbol='EURUSD', volume=0.01)

# Validate price
valid, error = validator.validate('price', symbol='EURUSD', price=1.1000)

# Validate stop loss
valid, error = validator.validate(
    'stop_loss',
    symbol='EURUSD',
    order_type='buy',
    entry_price=1.1000,
    stop_loss=1.0950
)

# Validate take profit
valid, error = validator.validate(
    'take_profit',
    symbol='EURUSD',
    order_type='buy',
    entry_price=1.1000,
    take_profit=1.1050
)

# Validate order type
valid, error = validator.validate('order_type', order_type='buy')

# Validate magic number
valid, error = validator.validate('magic', magic=12345)

# Validate deviation
valid, error = validator.validate('deviation', deviation=20)

# Validate expiration
valid, error = validator.validate('expiration', expiration=datetime.now())

# Validate timeframe
valid, error = validator.validate('timeframe', timeframe='H1')

# Validate date range
valid, error = validator.validate(
    'date_range',
    start_date=start,
    end_date=end
)
```

### Validate Complete Trade Request

```python
# Validate entire trade request
trade_request = {
    'symbol': 'EURUSD',
    'volume': 0.01,
    'order_type': 'buy',
    'price': 1.1000,
    'stop_loss': 1.0950,
    'take_profit': 1.1050,
    'deviation': 20,
    'magic': 12345,
    'comment': 'Test trade'
}

valid, errors = validator.validate('trade_request', **trade_request)

if not valid:
    print("Validation errors:")
    for error in errors:
        print(f"- {error}")
```

### Batch Validation

```python
# Validate multiple parameters at once
validations = [
    ('symbol', {'symbol': 'EURUSD'}),
    ('volume', {'symbol': 'EURUSD', 'volume': 0.01}),
    ('price', {'symbol': 'EURUSD', 'price': 1.1000}),
]

results = validator.validate_multiple(validations)

for validation_type, is_valid, error in results:
    if not is_valid:
        print(f"{validation_type}: {error}")
```

### Get Validation Rules

```python
# Get validation rules for specific parameter
rules = validator.get_validation_rules('volume')
print(rules)
# {
#     'min': 0.01,
#     'max': 100.0,
#     'step': 0.01,
#     'required': True
# }

# Get all validation rules
all_rules = validator.get_validation_rules()
```

---

## Utilities

### Time Operations

```python
from mymt5 import MT5Utils
from datetime import datetime

# Convert time formats
dt = MT5Utils.convert_time(1234567890, 'datetime')
timestamp = MT5Utils.convert_time(datetime.now(), 'timestamp')
iso_str = MT5Utils.convert_time(datetime.now(), 'iso')

# Get current time
current_time = MT5Utils.get_time('datetime')
current_timestamp = MT5Utils.get_time('timestamp')
```

### Price Operations

```python
# Convert price
price_float = MT5Utils.convert_price('1.10000')

# Format price
formatted = MT5Utils.format_price(1.1, 'EURUSD')  # '1.10000'

# Round price to symbol's digits
rounded = MT5Utils.round_price(1.100005, 'EURUSD')  # 1.10001
```

### Volume Operations

```python
# Convert volume
volume_float = MT5Utils.convert_volume('0.01')

# Round volume to symbol's volume step
rounded_vol = MT5Utils.round_volume(0.012, 'EURUSD')  # 0.01
```

### Data Formatting

```python
# Convert MT5 data to dict
data_dict = MT5Utils.to_dict(mt5_data)

# Convert to DataFrame
df = MT5Utils.to_dataframe(mt5_data)
```

### File Operations

```python
# Save data
MT5Utils.save(data, 'output.json', format='json')
MT5Utils.save(data, 'output.csv', format='csv')
MT5Utils.save(data, 'output.pkl', format='pickle')

# Load data
data = MT5Utils.load('output.json', format='json')
```

### Calculations

```python
# Calculate pip value
pip_value = MT5Utils.calculate('pip_value', 
    symbol='EURUSD',
    volume=1.0
)

# Calculate position profit
profit = MT5Utils.calculate('position_profit',
    symbol='EURUSD',
    volume=1.0,
    open_price=1.1000,
    close_price=1.1050
)

# Calculate margin requirement
margin = MT5Utils.calculate('margin',
    symbol='EURUSD',
    volume=1.0,
    leverage=100
)
```

---

## Best Practices

### 1. Always Use Context Managers or Try/Finally

```python
# Good - Using try/finally
client = MT5Client()
try:
    client.initialize(login=..., password=..., server=...)
    # Your code here
finally:
    client.shutdown()

# Better - Using context manager
from contextlib import contextmanager

@contextmanager
def mt5_connection(**creds):
    client = MT5Client()
    try:
        client.initialize(**creds)
        yield client
    finally:
        client.shutdown()

with mt5_connection(login=..., password=..., server=...) as client:
    # Your code here
    pass
```

### 2. Enable Auto-Reconnection

```python
client = MT5Client()
client.initialize(login=..., password=..., server=...)
client.enable_auto_reconnect()
client.set_retry_attempts(5)
client.set_retry_delay(3)
```

### 3. Always Validate Inputs

```python
validator = MT5Validator(client)

# Validate before trading
valid, error = validator.validate('symbol', 'EURUSD')
if not valid:
    print(f"Invalid symbol: {error}")
    return

valid, error = validator.validate('volume', symbol='EURUSD', volume=0.01)
if not valid:
    print(f"Invalid volume: {error}")
    return
```

### 4. Use Risk Management

```python
risk = MT5Risk(client, account_manager=MT5Account(client))

# Set limits
risk.set_limit('max_risk_per_trade', 2.0)
risk.set_limit('max_daily_loss', 500.0)
risk.set_limit('max_positions', 5)

# Calculate position size
size = risk.calculate_size(
    symbol='EURUSD',
    method='percent',
    risk_percent=1.0,
    entry_price=1.1000,
    stop_loss=1.0950
)

# Validate risk
violations = risk.validate(
    symbol='EURUSD',
    volume=size['volume'],
    entry_price=1.1000,
    stop_loss=1.0950
)

if not violations:
    # Execute trade
    trade.buy(symbol='EURUSD', volume=size['volume'], ...)
```

### 5. Handle Errors Gracefully

```python
try:
    result = trade.buy(symbol='EURUSD', volume=0.01, ...)
    if result['success']:
        print(f"Trade successful: {result['order']}")
    else:
        print(f"Trade failed: {result['error']}")
except Exception as e:
    print(f"Unexpected error: {e}")
    # Log error, send notification, etc.
```

### 6. Log Important Events

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log connections
if client.is_connected():
    logger.info("Connected to MT5")

# Log trades
result = trade.buy(...)
if result['success']:
    logger.info(f"Trade opened: {result['order']}")
else:
    logger.error(f"Trade failed: {result['error']}")
```

### 7. Use Symbol Manager for Symbol Operations

```python
# Initialize symbols before trading
symbol_manager = MT5Symbol(client)
symbol_manager.initialize('EURUSD')

# Check if tradable
if not symbol_manager.check('EURUSD', 'tradable'):
    print("Symbol not tradable")
    return

# Get current price before calculating SL/TP
current_price = symbol_manager.get_price('EURUSD', 'ask')
```

### 8. Monitor Account Health

```python
account = MT5Account(client)

# Check before trading
health = account.calculate('health')
if health['status'] != 'healthy':
    print("Account not healthy, skipping trade")
    return

# Check margin before trade
margin_level = account.calculate('margin_level')
if margin_level < 200:  # Your threshold
    print("Insufficient margin")
    return
```

---

## Advanced Topics

### Custom Trading Strategy Template

```python
class MyStrategy:
    def __init__(self, client):
        self.client = client
        self.account = MT5Account(client)
        self.symbol = MT5Symbol(client)
        self.data = MT5Data(client)
        self.trade = MT5Trade(client, symbol_manager=self.symbol)
        self.risk = MT5Risk(client, account_manager=self.account)
        
    def run(self):
        # Main strategy loop
        while True:
            try:
                # 1. Get market data
                bars = self.data.get_bars('EURUSD', 'M15', count=100)
                
                # 2. Generate signals
                signal = self.generate_signal(bars)
                
                # 3. Manage positions
                self.manage_positions()
                
                # 4. Execute trades
                if signal:
                    self.execute_trade(signal)
                    
                # 5. Wait for next iteration
                time.sleep(60)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
                
    def generate_signal(self, bars):
        # Your signal logic here
        pass
        
    def execute_trade(self, signal):
        # Calculate position size with risk management
        size = self.risk.calculate_size(
            symbol=signal['symbol'],
            method='percent',
            risk_percent=1.0,
            entry_price=signal['entry'],
            stop_loss=signal['sl']
        )
        
        # Execute trade
        if signal['direction'] == 'buy':
            self.trade.buy(
                symbol=signal['symbol'],
                volume=size['volume'],
                stop_loss=signal['sl'],
                take_profit=signal['tp']
            )
        else:
            self.trade.sell(
                symbol=signal['symbol'],
                volume=size['volume'],
                stop_loss=signal['sl'],
                take_profit=signal['tp']
            )
            
    def manage_positions(self):
        # Position management logic
        positions = self.trade.get_positions()
        for position in positions:
            # Trailing stop, break-even, etc.
            pass

# Run strategy
client = MT5Client()
client.initialize(login=..., password=..., server=...)

strategy = MyStrategy(client)
strategy.run()

client.shutdown()
```

### Multi-Symbol Trading

```python
symbols = ['EURUSD', 'GBPUSD', 'USDJPY']

# Initialize all symbols
for sym in symbols:
    symbol_manager.initialize(sym)

# Get data for all symbols
data_dict = {}
for sym in symbols:
    data_dict[sym] = data_manager.get_bars(sym, 'H1', count=100)

# Monitor all symbols
for sym in symbols:
    price = symbol_manager.get_price(sym, 'current')
    positions = trade_manager.get_positions(symbol=sym)
    print(f"{sym}: Price={price}, Positions={len(positions)}")
```

### Performance Monitoring

```python
import time

class PerformanceMonitor:
    def __init__(self, history_manager):
        self.history = history_manager
        
    def monitor(self, interval=3600):
        """Monitor performance every hour"""
        while True:
            # Get daily metrics
            win_rate = self.history.calculate('win_rate', days=1)
            profit = self.history.calculate('total_profit', days=1)
            trades = self.history.calculate('total_trades', days=1)
            
            print(f"Daily Stats:")
            print(f"  Win Rate: {win_rate}%")
            print(f"  Profit: ${profit}")
            print(f"  Trades: {trades}")
            
            # Check if daily loss limit exceeded
            if profit < -500:
                print("Daily loss limit exceeded!")
                # Stop trading, send notification, etc.
                
            time.sleep(interval)

# Usage
monitor = PerformanceMonitor(history_manager)
monitor.monitor(interval=3600)  # Check every hour
```

---

## Conclusion

This user guide covers the core functionality of MyMT5. For more information:

- **[API Reference](api_reference.md)**: Complete API documentation
- **[Examples](../examples/)**: Working code examples
- **[Troubleshooting](troubleshooting.md)**: Common issues and solutions
- **[Quick Start](quickstart.md)**: Get started quickly

Happy Trading! 📈

