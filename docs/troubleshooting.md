# MyMT5 Troubleshooting Guide

Common issues and their solutions for MyMT5 MetaTrader 5 Python trading system.

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Connection Issues](#connection-issues)
3. [Trading Issues](#trading-issues)
4. [Data Retrieval Issues](#data-retrieval-issues)
5. [Symbol Issues](#symbol-issues)
6. [Performance Issues](#performance-issues)
7. [Platform-Specific Issues](#platform-specific-issues)
8. [Error Messages](#error-messages)
9. [Debugging Tips](#debugging-tips)
10. [Getting Help](#getting-help)

---

## Installation Issues

### Module 'MetaTrader5' not found

**Problem**: `ModuleNotFoundError: No module named 'MetaTrader5'`

**Solution**:
```bash
pip install MetaTrader5
```

If still not working:
```bash
# Check Python environment
python -c "import sys; print(sys.path)"

# Reinstall in current environment
pip uninstall MetaTrader5
pip install MetaTrader5 --no-cache-dir
```

### Module 'mymt5' not found

**Problem**: `ModuleNotFoundError: No module named 'mymt5'`

**Solutions**:

1. **If installing from source**:
```bash
pip install -e path/to/mymt5
```

2. **If using package**:
```bash
pip install mymt5
```

3. **Verify installation**:
```python
import sys
print(sys.path)
# Make sure mymt5 path is in the list
```

4. **Check virtual environment**:
```bash
# Ensure you're in the right venv
which python  # Linux/macOS
where python  # Windows
```

### ImportError: DLL load failed

**Problem**: `ImportError: DLL load failed while importing mt5`

**Solution**:
```bash
# Reinstall Visual C++ Redistributable
# Download from Microsoft:
# https://aka.ms/vs/17/release/vc_redist.x64.exe

# Or install 32-bit version if needed
# https://aka.ms/vs/17/release/vc_redist.x86.exe
```

### pip install fails

**Problem**: `ERROR: Could not build wheels for package`

**Solutions**:

1. **Update pip**:
```bash
python -m pip install --upgrade pip setuptools wheel
```

2. **Install build tools**:
```bash
# Windows
# Install Visual Studio Build Tools
# https://visualstudio.microsoft.com/downloads/

# Linux
sudo apt install build-essential python3-dev

# macOS
xcode-select --install
```

---

## Connection Issues

### Failed to initialize MT5

**Problem**: `initialize() returned False`

**Common causes and solutions**:

#### 1. MT5 Not Installed

```bash
# Verify MT5 installation
# Windows: Check C:\Program Files\MetaTrader 5\
# Look for terminal64.exe

# If not installed, download from your broker
```

#### 2. Incorrect MT5 Path

```python
# Correct path in config.ini or code
client = MT5Client(
    path=r'C:\Program Files\MetaTrader 5\terminal64.exe'
)
```

#### 3. MT5 Already Running

**Solution**: Close all MT5 terminals and try again

```python
# Or use existing MT5 instance
client = MT5Client()
client.connect()  # Connect to running MT5
```

#### 4. Incorrect Credentials

```python
# Verify credentials
client.initialize(
    login=12345678,  # Correct account number
    password='YourPassword',  # Case-sensitive!
    server='YourBroker-Demo'  # Exact server name
)

# Get error details
if not client.is_connected():
    error = client.get_error()
    print(f"Error: {error}")
```

#### 5. MT5 Version Mismatch

```bash
# Update MT5 terminal to latest version
# In MT5: Help → Check for Updates

# Update MetaTrader5 package
pip install --upgrade MetaTrader5
```

### Connection drops randomly

**Problem**: Connection lost during operation

**Solutions**:

1. **Enable auto-reconnection**:
```python
client.enable_auto_reconnect()
client.set_retry_attempts(5)
client.set_retry_delay(3)
```

2. **Check internet connection**:
```python
import socket

def check_connection(host="8.8.8.8", port=53, timeout=3):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False

if not check_connection():
    print("No internet connection")
```

3. **Increase timeout**:
```python
client = MT5Client(timeout=120000)  # 120 seconds
```

4. **Monitor connection**:
```python
def on_disconnect(client):
    print("Disconnected! Reconnecting...")
    client.reconnect()

client.on('disconnect', on_disconnect)
```

### Authentication failed

**Problem**: Login fails with correct credentials

**Solutions**:

1. **Verify account status in MT5 terminal**:
   - Open MT5 manually
   - Try to login with same credentials
   - Check if account is locked/expired

2. **Check server name**:
```python
# Server name must match exactly
# Check in MT5: Tools → Options → Server

# Common formats:
server = 'BrokerName-Demo'
server = 'BrokerName-Live'
server = 'BrokerName-Demo01'
```

3. **Wait and retry**:
```python
import time

for attempt in range(3):
    success = client.initialize(login=..., password=..., server=...)
    if success:
        break
    print(f"Attempt {attempt + 1} failed, retrying...")
    time.sleep(5)
```

### Firewall blocking connection

**Problem**: Firewall prevents MT5 connection

**Solutions**:

1. **Allow MT5 in Windows Firewall**:
   - Windows Security → Firewall & network protection
   - Allow an app through firewall
   - Add `terminal64.exe`

2. **Check antivirus**:
   - Add MT5 folder to exclusions
   - Temporarily disable to test

3. **Check network restrictions**:
   - Some networks block trading platforms
   - Try different network or VPN

---

## Trading Issues

### Order execution failed

**Problem**: `execute() returns success=False`

**Common causes and solutions**:

#### 1. Invalid Symbol

```python
# Initialize symbol first
symbol = MT5Symbol(client)
symbol.initialize('EURUSD')

# Verify symbol exists
valid, error = symbol.validate('EURUSD', 'exists')
if not valid:
    print(f"Symbol error: {error}")
```

#### 2. Invalid Volume

```python
# Check volume constraints
info = symbol.get_info('EURUSD')
min_vol = info['volume_min']
max_vol = info['volume_max']
step = info['volume_step']

# Validate volume
valid, error = symbol.validate_volume('EURUSD', 0.01)
if not valid:
    print(f"Volume error: {error}")
```

#### 3. Market Closed

```python
# Check if market is open
is_open = symbol.check('EURUSD', 'market_open')
if not is_open:
    print("Market is closed")
```

#### 4. Insufficient Margin

```python
# Check margin before trading
account = MT5Account(client)
margin_free = account.get('margin_free')

# Calculate required margin
margin_required = account.calculate('margin_required',
    symbol='EURUSD',
    volume=0.01
)

if margin_required > margin_free:
    print("Insufficient margin")
```

#### 5. Invalid Stop Loss / Take Profit

```python
# Validate SL/TP
validator = MT5Validator(client)

valid, error = validator.validate('stop_loss',
    symbol='EURUSD',
    order_type='buy',
    entry_price=1.1000,
    stop_loss=1.0950
)

if not valid:
    print(f"SL error: {error}")
```

### Position not closing

**Problem**: `close_position()` fails

**Solutions**:

1. **Verify position exists**:
```python
positions = trade.get_positions(ticket=123456)
if not positions:
    print("Position not found")
```

2. **Check market status**:
```python
symbol = positions[0]['symbol']
is_open = symbol_manager.check(symbol, 'market_open')
if not is_open:
    print("Market closed, cannot close position")
```

3. **Close by symbol if ticket unknown**:
```python
# Close all positions for a symbol
trade.close_position(symbol='EURUSD')
```

4. **Handle partial closes**:
```python
# Close specific volume
result = trade.close_position(ticket=123456, volume=0.01)
```

### Orders not being placed

**Problem**: Pending orders not appearing

**Solutions**:

1. **Verify order type**:
```python
from mymt5.enums import OrderType

# Use correct order type
result = trade.execute(
    symbol='EURUSD',
    order_type=OrderType.BUY_LIMIT,  # Not 'buy_limit'
    volume=0.01,
    price=1.0950
)
```

2. **Check price validity**:
```python
# Limit order price must be better than current
current_price = symbol.get_price('EURUSD', 'ask')
limit_price = 1.0950

if limit_price >= current_price:  # For buy limit
    print("Limit price must be below current price")
```

3. **Validate request**:
```python
valid, errors = trade.validate_request({
    'symbol': 'EURUSD',
    'order_type': OrderType.BUY_LIMIT,
    'volume': 0.01,
    'price': 1.0950,
    'stop_loss': 1.0900,
    'take_profit': 1.1000
})

if not valid:
    print(f"Validation errors: {errors}")
```

---

## Data Retrieval Issues

### No data returned

**Problem**: `get_bars()` or `get_ticks()` returns empty

**Solutions**:

1. **Initialize symbol**:
```python
symbol = MT5Symbol(client)
symbol.initialize('EURUSD')
```

2. **Check date range**:
```python
from datetime import datetime, timedelta

# Use reasonable date range
end_date = datetime.now()
start_date = end_date - timedelta(days=7)  # Not years ago!

bars = data.get_bars('EURUSD', 'H1', start_date=start_date, end_date=end_date)
```

3. **Check timeframe**:
```python
# Use valid timeframe
timeframes = data.get_timeframes()
print(f"Available timeframes: {timeframes}")

# Correct usage
bars = data.get_bars('EURUSD', 'H1', count=100)  # Not 'h1' or '1H'
```

4. **Verify symbol has data**:
```python
# Not all symbols have historical data
# Try with major pairs first
bars = data.get_bars('EURUSD', 'H1', count=10)
if bars.empty:
    print("No data available for this symbol")
```

### Data appears incorrect

**Problem**: Strange prices or missing bars

**Solutions**:

1. **Clean data**:
```python
# Remove outliers and gaps
bars = data.process('clean', bars, std_threshold=3)
bars = data.process('fill_missing', bars, method='forward')
```

2. **Verify timeframe**:
```python
# Make sure you're using correct timeframe
print(f"Requested: H1")
print(f"Received: {bars.index[1] - bars.index[0]}")  # Should be 1 hour
```

3. **Check for gaps**:
```python
gaps = data.process('detect_gaps', bars)
if gaps:
    print(f"Found {len(gaps)} gaps in data")
```

### Streaming not working

**Problem**: `stream()` doesn't call callback

**Solutions**:

1. **Verify callback signature**:
```python
# Correct callback signature
def on_tick(tick):  # Single parameter
    print(tick)

# Not this
def on_tick():  # Missing parameter
    pass
```

2. **Keep script running**:
```python
import time

data.stream('ticks', symbol='EURUSD', callback=on_tick)

try:
    while True:
        time.sleep(1)  # Keep alive
except KeyboardInterrupt:
    data.stop_stream()
```

3. **Check interval**:
```python
# Use reasonable interval
data.stream('ticks', symbol='EURUSD', callback=on_tick, interval=1)  # 1 second
```

---

## Symbol Issues

### Symbol not found

**Problem**: `'EURUSD' not found`

**Solutions**:

1. **Check symbol name**:
```python
# Symbol names may vary by broker
# Common formats:
symbols = [
    'EURUSD',
    'EURUSDm',
    'EURUSD.a',
    'EUR/USD'
]

# List all available symbols
all_symbols = symbol_manager.get_symbols('all')
print([s['name'] for s in all_symbols if 'EUR' in s['name']])
```

2. **Initialize symbol**:
```python
symbol_manager.initialize('EURUSD')
```

3. **Add to Market Watch**:
```python
symbol_manager.manage('add', 'EURUSD')
```

### Symbol not tradable

**Problem**: Symbol exists but can't trade

**Solutions**:

1. **Check trading status**:
```python
tradable = symbol_manager.check('EURUSD', 'tradable')
print(f"Tradable: {tradable}")

# Get full info
info = symbol_manager.get_info('EURUSD')
print(f"Trade mode: {info['trade_mode']}")
print(f"Trade stops level: {info['trade_stops_level']}")
```

2. **Check account permissions**:
```python
account = MT5Account(client)
trade_allowed = account.check('trade_allowed')
if not trade_allowed:
    print("Trading not allowed for this account")
```

3. **Check market hours**:
```python
market_open = symbol_manager.check('EURUSD', 'market_open')
if not market_open:
    print("Market is currently closed")
```

---

## Performance Issues

### Slow data retrieval

**Problem**: `get_bars()` takes too long

**Solutions**:

1. **Use caching**:
```python
# Cache frequently used data
data.cache('eurusd_h1', bars, ttl=300)  # Cache for 5 minutes

# Retrieve from cache
cached = data.get_cached('eurusd_h1')
if cached is not None:
    bars = cached
else:
    bars = data.get_bars('EURUSD', 'H1', count=100)
    data.cache('eurusd_h1', bars, ttl=300)
```

2. **Limit data requests**:
```python
# Request only what you need
bars = data.get_bars('EURUSD', 'H1', count=100)  # Not 10000!
```

3. **Use appropriate timeframe**:
```python
# Higher timeframes = less data = faster
bars = data.get_bars('EURUSD', 'D1', count=100)  # Faster than M1
```

### High memory usage

**Problem**: Script uses too much memory

**Solutions**:

1. **Clear cache regularly**:
```python
data.clear_cache()
```

2. **Delete unused data**:
```python
del bars  # Free memory
import gc
gc.collect()
```

3. **Process data in chunks**:
```python
# Instead of loading all at once
for i in range(0, total_days, 7):
    start = datetime.now() - timedelta(days=i+7)
    end = datetime.now() - timedelta(days=i)
    bars = data.get_bars('EURUSD', 'H1', start_date=start, end_date=end)
    # Process bars
    del bars
```

### Script freezing

**Problem**: Script becomes unresponsive

**Solutions**:

1. **Use threading for long operations**:
```python
import threading

def fetch_data():
    bars = data.get_bars('EURUSD', 'M1', count=10000)
    # Process bars

thread = threading.Thread(target=fetch_data)
thread.start()
```

2. **Add timeout to operations**:
```python
import signal

def timeout_handler(signum, frame):
    raise TimeoutError("Operation timed out")

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(30)  # 30 second timeout

try:
    bars = data.get_bars('EURUSD', 'H1', count=100)
finally:
    signal.alarm(0)  # Cancel timeout
```

3. **Monitor resource usage**:
```python
import psutil
import os

process = psutil.Process(os.getpid())
print(f"Memory usage: {process.memory_info().rss / 1024 / 1024:.2f} MB")
print(f"CPU usage: {process.cpu_percent()}%")
```

---

## Platform-Specific Issues

### Linux: MT5 not working with Wine

**Problem**: MT5 doesn't start or crashes with Wine

**Solutions**:

1. **Use correct Wine prefix**:
```bash
export WINEPREFIX=~/.wine
export WINEARCH=win64
```

2. **Install dependencies**:
```bash
winetricks corefonts
winetricks vcrun2015
```

3. **Run headless**:
```bash
xvfb-run wine terminal64.exe
```

4. **Check Wine version**:
```bash
wine --version  # Should be 6.0+
```

### macOS: Wine issues

**Problem**: MT5 not working on macOS

**Solutions**:

1. **Use CrossOver** (paid alternative to Wine):
   - More stable on macOS
   - Better support

2. **Use Virtual Machine**:
   - VMware Fusion or Parallels
   - Windows 10/11 VM
   - More reliable

3. **For Apple Silicon (M1/M2)**:
   - Use Parallels with Windows ARM
   - Or use cloud-based solution

### Windows: Permission denied errors

**Problem**: `PermissionError` when accessing files

**Solutions**:

1. **Run as Administrator**:
   - Right-click terminal → Run as administrator

2. **Check file permissions**:
```python
import os
os.chmod('file.txt', 0o666)
```

3. **Close other programs**:
   - Make sure files aren't open in Excel, MT5, etc.

---

## Error Messages

### "retcode != TRADE_RETCODE_DONE"

**Meaning**: Trade request rejected

**Common return codes**:
- `TRADE_RETCODE_REJECT`: Request rejected
- `TRADE_RETCODE_INVALID_VOLUME`: Invalid volume
- `TRADE_RETCODE_INVALID_PRICE`: Invalid price
- `TRADE_RETCODE_INVALID_STOPS`: Invalid SL/TP
- `TRADE_RETCODE_NO_MONEY`: Insufficient funds
- `TRADE_RETCODE_MARKET_CLOSED`: Market closed
- `TRADE_RETCODE_REQUOTE`: Price changed, retry

**Solution**: Check the specific return code and error message:
```python
result = trade.buy(...)
if not result['success']:
    print(f"Error code: {result.get('retcode')}")
    print(f"Error message: {result.get('error')}")
```

### "symbol select error"

**Meaning**: Symbol not found or not in Market Watch

**Solution**:
```python
symbol_manager.initialize('EURUSD')
```

### "margin calculation error"

**Meaning**: Cannot calculate margin for order

**Solutions**:
1. Check if symbol is initialized
2. Verify volume is valid
3. Check account currency matches

### "invalid timeframe"

**Meaning**: Timeframe not recognized

**Solution**: Use correct timeframe string:
```python
# Correct
timeframes = ['M1', 'M5', 'M15', 'M30', 'H1', 'H4', 'D1', 'W1', 'MN1']

# Incorrect
bad_timeframes = ['1M', '5M', '1H', '1D', 'm1', 'h1']
```

---

## Debugging Tips

### Enable Detailed Logging

```python
import logging

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)

# Log everything
logger = logging.getLogger(__name__)
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

### Use Try-Except with Details

```python
try:
    result = trade.buy('EURUSD', 0.01)
except Exception as e:
    print(f"Exception type: {type(e).__name__}")
    print(f"Exception message: {str(e)}")
    import traceback
    traceback.print_exc()
```

### Check MT5 Terminal Info

```python
terminal = MT5Terminal(client)
info = terminal.get()

print("MT5 Terminal Info:")
for key, value in info.items():
    print(f"  {key}: {value}")
```

### Test Connection Continuously

```python
import time

while True:
    if client.is_connected():
        print("✓ Connected")
    else:
        print("✗ Disconnected")
        client.reconnect()
    
    time.sleep(5)
```

### Monitor Trade Execution

```python
def log_trade_result(result):
    print(f"\n{'='*50}")
    print(f"Trade Result:")
    print(f"  Success: {result.get('success')}")
    print(f"  Order: {result.get('order')}")
    print(f"  Volume: {result.get('volume')}")
    print(f"  Price: {result.get('price')}")
    print(f"  Retcode: {result.get('retcode')}")
    print(f"  Error: {result.get('error')}")
    print(f"{'='*50}\n")

result = trade.buy('EURUSD', 0.01)
log_trade_result(result)
```

### Create Debug Script

```python
# debug.py
from mymt5 import *
import logging

logging.basicConfig(level=logging.DEBUG)

def debug_environment():
    """Print environment info"""
    import sys
    import MetaTrader5 as mt5
    
    print("="*50)
    print("ENVIRONMENT INFO")
    print("="*50)
    print(f"Python version: {sys.version}")
    print(f"MT5 module version: {mt5.__version__}")
    print(f"Python path: {sys.executable}")
    print()

def debug_connection(login, password, server):
    """Test connection"""
    print("="*50)
    print("CONNECTION TEST")
    print("="*50)
    
    client = MT5Client()
    success = client.initialize(login=login, password=password, server=server)
    
    print(f"Connected: {client.is_connected()}")
    print(f"State: {client.connection_state}")
    
    if not success:
        error = client.get_error()
        print(f"Error: {error}")
    
    client.shutdown()
    print()

def debug_symbol(symbol_name):
    """Test symbol"""
    print("="*50)
    print(f"SYMBOL TEST: {symbol_name}")
    print("="*50)
    
    # Your connection code here
    client = MT5Client()
    client.initialize(...)
    
    symbol = MT5Symbol(client)
    
    exists = symbol.check(symbol_name, 'exists')
    print(f"Exists: {exists}")
    
    if exists:
        info = symbol.get_info(symbol_name)
        print(f"Digits: {info['digits']}")
        print(f"Point: {info['point']}")
        print(f"Min volume: {info['volume_min']}")
    
    client.shutdown()
    print()

if __name__ == '__main__':
    debug_environment()
    debug_connection(login=..., password=..., server=...)
    debug_symbol('EURUSD')
```

---

## Getting Help

### 1. Check Documentation
- [Quick Start Guide](quickstart.md)
- [User Guide](user_guide.md)
- [Installation Guide](installation.md)
- [API Reference](api_reference.md)

### 2. Search Examples
- Browse `examples/` directory
- Look for similar use cases

### 3. Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 4. Check MT5 Terminal
- Open MT5 manually
- Check Experts log
- Verify account works

### 5. Search Online
- [MQL5 Documentation](https://www.mql5.com/en/docs/python_metatrader5)
- [MQL5 Forum](https://www.mql5.com/en/forum)
- Stack Overflow

### 6. Create Minimal Reproduction

```python
# minimal_test.py - Share this when asking for help
from mymt5 import MT5Client

client = MT5Client()
success = client.initialize(
    login=12345678,  # Use demo account
    password='password',
    server='Broker-Demo'
)

print(f"Connected: {success}")
print(f"Error: {client.get_error()}")

client.shutdown()
```

---

## Still Having Issues?

If you've tried the solutions above and still have problems:

1. **Gather information**:
   - Error messages (full text)
   - Python version
   - MT5 version
   - Operating system
   - What you've tried

2. **Create minimal reproduction**:
   - Simplest code that shows the problem
   - Remove unnecessary code

3. **Ask for help**:
   - GitHub Issues (if available)
   - MQL5 Forum
   - Stack Overflow with tag `metatrader5`

Remember to **never share** your real credentials or sensitive information!

---

**Good luck troubleshooting!** Most issues can be resolved with the solutions above. 🔧

