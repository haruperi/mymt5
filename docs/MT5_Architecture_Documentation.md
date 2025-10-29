# MT5 Trading System - Class Architecture Documentation

## Overview
This document describes the architecture of a comprehensive MetaTrader 5 (MT5) Python trading system designed with clean, maintainable, and efficient code principles.

## Design Principles

### 1. **Unified Interface Pattern**
Instead of multiple specific methods, we use unified getters with parameters:
- `get(attribute)` instead of `get_balance()`, `get_equity()`, etc.
- `calculate(metric)` instead of separate calculation methods
- `check(check_type)` instead of multiple boolean methods

### 2. **Action-Based Methods**
Methods that perform actions use a type parameter:
- `execute(action, ...)` for all order types
- `manage(symbol, action)` for symbol operations
- `process(data, operation)` for data processing

### 3. **Flexible Filtering**
Common pattern using `filter_type` and `filter_value`:
- `get_positions(filter_type='symbol', filter_value='EURUSD')`
- `get_orders(filter_type='magic', filter_value=12345)`

### 4. **Dependency Injection**
Classes receive their dependencies through constructors:
- Promotes testability
- Reduces tight coupling
- Makes dependencies explicit

## System Architecture

### Layer Structure

```
┌─────────────────────────────────────────┐
│           Core Layer                     │
│         (MT5Client)                      │
└─────────────────────────────────────────┘
            ↓ provides connection
┌─────────────────────────────────────────┐
│       Information Layer                  │
│  (Account, Symbol, Terminal)             │
└─────────────────────────────────────────┘
            ↓ provides data
┌─────────────────────────────────────────┐
│         Data Layer                       │
│      (Data, History)                     │
└─────────────────────────────────────────┘
            ↓ enables trading
┌─────────────────────────────────────────┐
│       Trading Layer                      │
│       (Trade, Risk)                      │
└─────────────────────────────────────────┘
            ↓ supported by
┌─────────────────────────────────────────┐
│       Utility Layer                      │
│    (Validator, Utils)                    │
└─────────────────────────────────────────┘
```

## Class Descriptions

### Core Layer

#### MT5Client
**Purpose**: Central connection manager and configuration hub

**Responsibilities**:
- Establish and maintain connection to MT5 terminal
- Handle authentication and login
- Manage auto-reconnection logic
- Handle multiple accounts
- Event callback system
- Error handling and logging

**Key Methods**:
- `initialize()` - Initialize MT5 connection
- `login()` - Authenticate with credentials
- `connect()` - Establish connection with retry logic
- `on(event, callback)` - Register event handlers
- `configure()` - Set configuration parameters

**Usage Example**:
```python
client = MT5Client(config_path='config.json', auto_reconnect=True)
client.initialize()
client.login(account=12345, password='pass', server='Broker-Server')
client.on('disconnect', lambda: print('Disconnected!'))
```

---

### Information Layer

#### MT5Account
**Purpose**: Account information and status management

**Responsibilities**:
- Retrieve account information
- Calculate account metrics
- Validate credentials
- Monitor account health

**Key Methods**:
- `get(attribute)` - Unified getter for all account data
- `check(check_type)` - Status checks (demo, authorized, etc.)
- `calculate(metric)` - Calculate metrics (margin level, drawdown)

**Usage Example**:
```python
account = MT5Account(client)
balance = account.get('balance')
all_info = account.get()  # Returns complete dict
is_demo = account.check('demo')
margin_level = account.calculate('margin_level')
```

---

#### MT5Symbol
**Purpose**: Symbol management and market information

**Responsibilities**:
- Manage market watch
- Retrieve symbol information
- Get real-time prices
- Handle symbol subscriptions

**Key Methods**:
- `get_symbols(filter_type, filter_value)` - List symbols
- `get_info(symbol, attribute)` - Symbol information
- `get_price(symbol, price_type)` - Real-time prices
- `subscribe(symbol, callback)` - Subscribe to updates

**Usage Example**:
```python
symbol = MT5Symbol(client)
symbols = symbol.get_symbols('group', 'Forex*')
symbol.initialize(['EURUSD', 'GBPUSD'])
info = symbol.get_info('EURUSD', 'pip_value')
price = symbol.get_price('EURUSD', 'bid')
```

---

#### MT5Terminal
**Purpose**: Terminal information and status

**Responsibilities**:
- Retrieve terminal information
- Check terminal status
- Get terminal properties

**Key Methods**:
- `get(attribute)` - Terminal information
- `check(check_type)` - Status checks
- `get_properties(property_type)` - System properties

**Usage Example**:
```python
terminal = MT5Terminal(client)
version = terminal.get('version')
is_connected = terminal.check('connected')
resources = terminal.get_properties('resources')
```

---

### Data Layer

#### MT5Data
**Purpose**: Historical and real-time market data management

**Responsibilities**:
- Fetch OHLCV bars
- Fetch tick data
- Stream real-time data
- Cache data
- Process and clean data

**Key Methods**:
- `get_bars(symbol, timeframe, ...)` - Get historical bars
- `get_ticks(symbol, ...)` - Get tick data
- `stream(symbol, callback)` - Real-time streaming
- `process(data, operation)` - Data processing
- `cache()` / `get_cached()` - Caching operations

**Usage Example**:
```python
data = MT5Data(client)
# Get last 100 bars
bars = data.get_bars('EURUSD', 'H1', count=100)
# Get date range
bars = data.get_bars('EURUSD', 'D1', 
                     start=datetime(2024,1,1), 
                     end=datetime(2024,12,31))
# Process data
clean_data = data.process(bars, 'clean')
# Stream ticks
data.stream('EURUSD', lambda tick: print(tick), 'ticks')
```

---

#### MT5History
**Purpose**: Trade history and performance analytics

**Responsibilities**:
- Retrieve historical deals and orders
- Calculate performance metrics
- Generate reports
- Analyze trading patterns

**Key Methods**:
- `get(history_type, start, end)` - Get history
- `calculate(metric)` - Calculate performance metrics
- `analyze(analysis_type)` - Analyze patterns
- `generate_report(report_type)` - Create reports

**Usage Example**:
```python
history = MT5History(client)
deals = history.get('deals', start=datetime(2024,1,1))
win_rate = history.calculate('win_rate')
analysis = history.analyze('by_symbol')
report = history.generate_report('performance', format='dict')
```

---

### Trading Layer

#### MT5Trade
**Purpose**: Unified trading interface for orders and positions

**Responsibilities**:
- Execute market and pending orders
- Manage positions
- Modify orders and positions
- Close positions
- Calculate position metrics

**Key Methods**:
- `execute(action, symbol, volume, ...)` - Unified order execution
- `buy()` / `sell()` - Simplified market orders
- `get_orders()` / `get_positions()` - Retrieve orders/positions
- `modify_order()` / `modify_position()` - Modifications
- `close_position()` - Close positions
- `analyze_position(ticket, metric)` - Position analytics

**Usage Example**:
```python
trade = MT5Trade(client, symbol_manager)

# Market order
result = trade.buy('EURUSD', 0.1, sl=1.0800, tp=1.1000)

# Pending order
result = trade.execute('buy_limit', 'EURUSD', 0.1, 
                       price=1.0900, sl=1.0850, tp=1.1000)

# Get positions
positions = trade.get_positions('symbol', 'EURUSD')

# Modify position
trade.modify_position(ticket=123456, sl=1.0850, tp=1.1050)

# Close position
trade.close_position(ticket=123456)

# Analyze
profit = trade.analyze_position(123456, 'profit')
stats = trade.get_position_stats('symbol', 'EURUSD')
```

---

#### MT5Risk
**Purpose**: Risk management and position sizing

**Responsibilities**:
- Calculate position sizes
- Calculate risk metrics
- Validate risk limits
- Check portfolio risk

**Key Methods**:
- `calculate_size(symbol, risk, sl, method)` - Position sizing
- `calculate_risk(symbol, volume, sl, metric)` - Risk calculation
- `set_limit()` / `get_limit()` - Manage risk limits
- `validate(symbol, volume, sl, tp)` - Validate trades
- `get_portfolio_risk(metric)` - Portfolio risk metrics

**Usage Example**:
```python
risk = MT5Risk(client, account_manager, symbol_manager)

# Calculate position size for 1% risk
size = risk.calculate_size('EURUSD', risk=1, sl=50, method='percent')

# Calculate risk for a trade
risk_amount = risk.calculate_risk('EURUSD', 0.1, sl=50, metric='amount')

# Set limits
risk.set_limit('max_risk_per_trade', 2.0)
risk.set_limit('max_daily_loss', 500)

# Validate trade
is_valid, violations = risk.validate('EURUSD', 0.1, sl=1.0850, tp=1.1000)

# Portfolio risk
total_exposure = risk.get_portfolio_risk('total_exposure')
```

---

### Utility Layer

#### MT5Validator
**Purpose**: Input validation and business rule enforcement

**Responsibilities**:
- Validate all inputs
- Enforce business rules
- Check constraints

**Key Methods**:
- `validate(validation_type, **kwargs)` - Unified validation
- `validate_multiple(validations)` - Batch validation

**Usage Example**:
```python
validator = MT5Validator(symbol_manager)

# Validate symbol
is_valid, error = validator.validate('symbol', symbol='EURUSD')

# Validate volume
is_valid, error = validator.validate('volume', 
                                     symbol='EURUSD', 
                                     volume=0.1)

# Validate stop loss
is_valid, error = validator.validate('stop_loss',
                                     symbol='EURUSD',
                                     entry_price=1.0900,
                                     sl_price=1.0850,
                                     order_type='buy')

# Batch validation
validations = [
    ('symbol', {'symbol': 'EURUSD'}),
    ('volume', {'symbol': 'EURUSD', 'volume': 0.1}),
]
results = validator.validate_multiple(validations)
```

---

#### MT5Utils
**Purpose**: Static utility functions

**Responsibilities**:
- Type conversions
- Formatting
- File I/O
- Calculations

**Key Methods**:
- `convert_time()` - Time conversions
- `convert_price()` - Price/points/pips conversions
- `convert_volume()` - Volume conversions
- `to_dict()` / `to_dataframe()` - Data structure conversions
- `save()` / `load()` - File operations

**Usage Example**:
```python
# Time conversion
mt5_time = MT5Utils.convert_time(datetime.now(), 'datetime', 'mt5')

# Price conversion
points = MT5Utils.convert_price('EURUSD', 0.0010, 'price', 'points')

# Rounding
price = MT5Utils.round_price('EURUSD', 1.09123)

# Data conversion
position_dict = MT5Utils.to_dict(position_obj, 'position')
df = MT5Utils.to_dataframe(bars_list, 'bars')

# File operations
MT5Utils.save(data, 'data.json', format='json')
data = MT5Utils.load('data.json', format='json')
```

---

## Enumerations

### ConnectionState
```python
class ConnectionState(Enum):
    DISCONNECTED = 0
    CONNECTED = 1
    FAILED = 2
    INITIALIZING = 3
    RECONNECTING = 4
```

### OrderType
```python
class OrderType(Enum):
    BUY = 'buy'
    SELL = 'sell'
    BUY_LIMIT = 'buy_limit'
    SELL_LIMIT = 'sell_limit'
    BUY_STOP = 'buy_stop'
    SELL_STOP = 'sell_stop'
    BUY_STOP_LIMIT = 'buy_stop_limit'
    SELL_STOP_LIMIT = 'sell_stop_limit'
```

### TimeFrame
```python
class TimeFrame(Enum):
    M1 = mt5.TIMEFRAME_M1
    M5 = mt5.TIMEFRAME_M5
    M15 = mt5.TIMEFRAME_M15
    M30 = mt5.TIMEFRAME_M30
    H1 = mt5.TIMEFRAME_H1
    H4 = mt5.TIMEFRAME_H4
    D1 = mt5.TIMEFRAME_D1
    W1 = mt5.TIMEFRAME_W1
    MN1 = mt5.TIMEFRAME_MN1
```

---

## Usage Workflow

### 1. Basic Setup
```python
from mt5_system import MT5Client, MT5Account, MT5Symbol, MT5Trade

# Initialize client
client = MT5Client(auto_reconnect=True)
client.initialize()
client.login(account=12345, password='password', server='Broker-Server')

# Setup managers
account = MT5Account(client)
symbol = MT5Symbol(client)
trade = MT5Trade(client, symbol)
```

### 2. Get Market Information
```python
# Account info
balance = account.get('balance')
equity = account.get('equity')

# Symbol info
symbol.initialize(['EURUSD', 'GBPUSD'])
bid = symbol.get_price('EURUSD', 'bid')
pip_value = symbol.get_info('EURUSD', 'pip_value')
```

### 3. Execute Trade
```python
# Calculate position size
risk_manager = MT5Risk(client, account, symbol)
lot_size = risk_manager.calculate_size('EURUSD', risk=1, sl=50)

# Execute trade
result = trade.buy('EURUSD', lot_size, sl=1.0850, tp=1.1000)

if result['retcode'] == mt5.TRADE_RETCODE_DONE:
    print(f"Order placed: {result['order']}")
```

### 4. Monitor Positions
```python
# Get all positions
positions = trade.get_positions()

# Get positions for specific symbol
eur_positions = trade.get_positions('symbol', 'EURUSD')

# Analyze position
for pos in eur_positions:
    profit = trade.analyze_position(pos.ticket, 'profit')
    print(f"Position {pos.ticket}: ${profit:.2f}")
```

### 5. Historical Analysis
```python
history = MT5History(client)

# Get month performance
deals = history.get_period('month')
win_rate = history.calculate('win_rate')
profit_factor = history.calculate('profit_factor')

# Generate report
report = history.generate_report('performance', format='dict')
print(f"Win Rate: {report['win_rate']:.2%}")
print(f"Profit Factor: {report['profit_factor']:.2f}")
```

---

## Error Handling

All methods follow consistent error handling:

### Return Patterns

#### Boolean Returns
```python
success = client.connect()
if not success:
    error = client.get_error()
    print(f"Error: {error['description']}")
```

#### Dict Returns (Trade Results)
```python
result = trade.buy('EURUSD', 0.1)
if result['retcode'] != mt5.TRADE_RETCODE_DONE:
    print(f"Trade failed: {result['comment']}")
```

#### Tuple Returns (Validation)
```python
is_valid, error_msg = validator.validate('symbol', symbol='EURUSD')
if not is_valid:
    print(f"Validation error: {error_msg}")
```

---

## Configuration File Structure

### config.json
```json
{
  "connection": {
    "path": null,
    "timeout": 60000,
    "portable": false,
    "auto_reconnect": true,
    "retry_attempts": 3,
    "retry_delay": 5
  },
  "accounts": {
    "default": {
      "account": 12345,
      "password": "password",
      "server": "Broker-Server"
    }
  },
  "risk": {
    "max_risk_per_trade": 1.0,
    "max_daily_loss": 500,
    "max_positions": 10,
    "max_symbol_positions": 3
  },
  "logging": {
    "level": "INFO",
    "file": "mt5_system.log",
    "max_size": 10485760,
    "backup_count": 5
  }
}
```

---

## Testing Strategy

### Unit Tests
Test each class independently with mocked dependencies:
```python
def test_account_get_balance():
    mock_client = Mock()
    mock_client.is_connected.return_value = True
    account = MT5Account(mock_client)
    # Test implementation
```

### Integration Tests
Test interactions between classes:
```python
def test_trade_execution_workflow():
    client = MT5Client()
    account = MT5Account(client)
    symbol = MT5Symbol(client)
    trade = MT5Trade(client, symbol)
    # Test complete workflow
```

---

## Performance Considerations

1. **Caching**: Symbol and account information is cached
2. **Batch Operations**: Use batch methods when possible
3. **Event-Driven**: Use callbacks for real-time updates
4. **Lazy Loading**: Data fetched only when needed

---

## Extension Points

The system is designed to be extensible:

1. **Custom Strategies**: Inherit from base classes
2. **Additional Validators**: Extend MT5Validator
3. **Custom Utilities**: Add to MT5Utils
4. **Event Handlers**: Register custom callbacks

---

## Deployment

### Production Checklist
- [ ] Configure logging appropriately
- [ ] Set up auto-reconnection
- [ ] Configure risk limits
- [ ] Test error handling
- [ ] Set up monitoring
- [ ] Configure backup accounts
- [ ] Test disaster recovery

---

## Support & Maintenance

### Logging
All operations are logged with appropriate levels:
- DEBUG: Detailed operation info
- INFO: Normal operations
- WARNING: Recoverable issues
- ERROR: Serious problems

### Monitoring
Monitor these key metrics:
- Connection uptime
- Error rates
- Trade execution success rate
- Average latency
- Resource usage

---

## Conclusion

This architecture provides:
- ✅ Clean, maintainable code
- ✅ Comprehensive functionality
- ✅ Flexible and extensible
- ✅ Well-documented
- ✅ Easy to test
- ✅ Production-ready

Total: **10 Classes**, **~120 Methods**, **Full MT5 Trading Capability**
