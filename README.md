# MyMT5 - MetaTrader 5 Python Trading System

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A comprehensive, production-ready Python library for interacting with MetaTrader 5 terminal. Built with clean architecture, extensive error handling, and comprehensive testing.

## ✨ Features

### 🔌 Connection Management
- Robust connection handling with automatic reconnection
- Multi-account support with easy account switching
- Event-driven architecture for connection events
- Connection pooling and state management

### 📊 Market Data
- Real-time price streaming
- Historical OHLCV data (bars/candles)
- Tick-by-tick data retrieval
- Data caching for performance optimization
- Multiple export formats (CSV, JSON, Parquet)

### 💼 Trading Operations
- Market orders (Buy/Sell)
- Pending orders (Limit, Stop, Stop-Limit)
- Position management (Modify, Close, Reverse)
- Order management (Modify, Cancel)
- Batch operations support

### 🛡️ Risk Management
- Position sizing based on risk percentage or fixed amount
- Risk/reward ratio calculations
- Portfolio risk analytics
- Margin validation
- Configurable risk limits per trade, day, and portfolio

### 📈 Historical Analysis
- Performance metrics (Win rate, Profit factor, Sharpe ratio)
- Trade analysis by symbol, time, and strategy
- Maximum drawdown calculations
- Comprehensive reporting (Performance, Trade log, Summary)
- Export to multiple formats

### ✅ Validation
- Comprehensive parameter validation
- Symbol validation (existence, tradability)
- Volume validation (min, max, step)
- Price and stop level validation
- Complete trade request validation

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/mymt5.git
cd mymt5

# Create and activate virtual environment
python -m venv venv

# On Windows:
venv\Scripts\activate

# On Linux/Mac:
source venv/bin/activate

# Install the package
pip install -e .
```

### Basic Usage

```python
from mymt5 import MT5Client, MT5Account, MT5Symbol, MT5Trade

# 1. Initialize client and connect
client = MT5Client()
client.initialize(
    login=12345678,
    password='YourPassword',
    server='YourBroker-Demo'
)

# 2. Get account information
account = MT5Account(client)
balance = account.get('balance')
equity = account.get('equity')
print(f"Balance: ${balance}, Equity: ${equity}")

# 3. Get market data
symbol = MT5Symbol(client)
price = symbol.get_price('EURUSD', 'bid')
print(f"EUR/USD: {price}")

# 4. Execute a trade
trade = MT5Trade(client, symbol_manager=symbol)
result = trade.buy(
    symbol='EURUSD',
    volume=0.01,
    stop_loss=1.0950,
    take_profit=1.1050,
    comment='My first trade'
)

if result['success']:
    print(f"✓ Trade opened: {result['order']}")
else:
    print(f"✗ Trade failed: {result['error']}")

# 5. Cleanup
client.shutdown()
```

### Using Configuration File

Create `config.ini`:

```ini
[MT5]
login=12345678
password=YourPassword
server=YourBroker-Demo
path=C:\Program Files\MetaTrader 5\terminal64.exe
timeout=60000

[RISK]
max_risk_per_trade=2.0
max_daily_loss=500.0
max_positions=5
```

**Important**: Add `config.ini` to your `.gitignore`!

```python
import configparser
from mymt5 import MT5Client

# Load configuration
config = configparser.ConfigParser()
config.read('config.ini')

# Initialize with config
client = MT5Client(
    path=config['MT5'].get('path'),
    timeout=int(config['MT5'].get('timeout', 60000))
)

client.initialize(
    login=int(config['MT5']['login']),
    password=config['MT5']['password'],
    server=config['MT5']['server']
)
```

## 📚 Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[Quick Start Guide](docs/quickstart.md)** - Get started in minutes
- **[User Guide](docs/user_guide.md)** - Complete feature documentation
- **[Installation Guide](docs/installation.md)** - Detailed installation instructions
- **[API Reference](docs/api_reference.md)** - Complete API documentation
- **[Troubleshooting](docs/troubleshooting.md)** - Common issues and solutions
- **[Configuration Guide](docs/configuration.md)** - Advanced configuration options

## 📖 Examples

Explore the `examples/` directory for comprehensive examples:

### Basic Examples
- `01_basic_connection.py` - Basic connection and initialization
- `02_account_info.py` - Account information and management
- `03_market_data.py` - Market data retrieval
- `03_symbol_management.py` - Symbol operations
- `04_terminal_info.py` - Terminal information

### Trading Examples
- `04_simple_trade.py` - Simple trading operations
- `05_risk_management.py` - Risk management examples
- `07_trading_operations.py` - Advanced trading operations
- `08_validation.py` - Input validation examples

### Data Examples
- `05_data_management.py` - Data retrieval and management
- `06_history_analysis.py` - Historical analysis
- `07_streaming_data.py` - Real-time data streaming

### Advanced Examples
- `09_strategy_template.py` - Trading strategy template
- `10_advanced_trading.py` - Advanced trading techniques

Run any example:

```bash
python examples/01_basic_connection.py
```

## 🏗️ Architecture

MyMT5 follows a layered architecture:

```
┌─────────────────────────────────┐
│      Core Layer                 │
│      MT5Client                  │ ← Connection, Auth, Events
└─────────────────────────────────┘
           ↓
┌─────────────────────────────────┐
│   Information Layer             │
│   Account │ Symbol │ Terminal   │ ← Info Retrieval
└─────────────────────────────────┘
           ↓
┌─────────────────────────────────┐
│      Data Layer                 │
│      Data │ History             │ ← Market Data
└─────────────────────────────────┘
           ↓
┌─────────────────────────────────┐
│    Trading Layer                │
│      Trade │ Risk               │ ← Trading Operations
└─────────────────────────────────┘
           ↓
┌─────────────────────────────────┐
│    Utility Layer                │
│   Validator │ Utils             │ ← Utilities
└─────────────────────────────────┘
```

### Core Components

- **MT5Client**: Connection management, authentication, multi-account support
- **MT5Account**: Account information, metrics, health monitoring
- **MT5Symbol**: Symbol operations, price retrieval, market watch management
- **MT5Terminal**: Terminal information and status
- **MT5Data**: Market data retrieval, caching, streaming
- **MT5History**: Historical data, performance analysis, reporting
- **MT5Trade**: Order execution, position management, trade operations
- **MT5Risk**: Position sizing, risk calculations, portfolio analytics
- **MT5Validator**: Parameter validation, trade request validation
- **MT5Utils**: Utility functions for time, price, volume operations

## 🛠️ Development

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=mymt5 --cov-report=html

# Run specific test file
pytest tests/test_client.py -v

# Run integration tests
pytest tests/test_integration.py -v

# Run performance tests
pytest tests/test_performance.py -v
```

### Code Quality

```bash
# Format code
black mymt5/ tests/

# Run linter
flake8 mymt5/ tests/

# Type checking
mypy mymt5/
```

### Project Structure

```
mymt5/
├── mymt5/                  # Main package
│   ├── __init__.py
│   ├── client.py          # Connection management
│   ├── account.py         # Account operations
│   ├── symbol.py          # Symbol operations
│   ├── terminal.py        # Terminal info
│   ├── data.py            # Market data
│   ├── history.py         # Historical analysis
│   ├── trade.py           # Trading operations
│   ├── risk.py            # Risk management
│   ├── validator.py       # Validation
│   ├── utils.py           # Utilities
│   └── enums.py           # Enumerations
├── tests/                 # Test suite
├── examples/              # Usage examples
├── docs/                  # Documentation
├── config.ini.example     # Config template
├── requirements.txt       # Dependencies
├── setup.py              # Package setup
└── README.md             # This file
```

## 📋 Requirements

- **Python 3.8+** (Python 3.10+ recommended)
- **MetaTrader 5 Terminal** (latest version)
- **Operating System**: Windows 10/11 (recommended), Linux with Wine, macOS with Wine/VM

### Python Dependencies

- `MetaTrader5` - Official MT5 Python integration
- `pandas` - Data manipulation and analysis
- `numpy` - Numerical computing
- `python-dateutil` - Date/time utilities

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`pytest tests/`)
6. Format code (`black mymt5/`)
7. Commit changes (`git commit -m 'Add amazing feature'`)
8. Push to branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

See [CONTRIBUTING.md](docs/contributing.md) for detailed guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- MetaTrader 5 Python API by MetaQuotes
- All contributors and users of this library

## 📞 Support

- **Documentation**: See [docs/](docs/) directory
- **Examples**: See [examples/](examples/) directory
- **Issues**: [GitHub Issues](https://github.com/yourusername/mymt5/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/mymt5/discussions)

## ⚠️ Disclaimer

This software is for educational and research purposes only. Trading financial instruments involves substantial risk of loss. Use at your own risk. The authors and contributors are not responsible for any financial losses incurred while using this software.

Always test strategies on a demo account before trading with real money.

## 🔖 Version

Current Version: **1.0.0**

See [CHANGELOG.md](CHANGELOG.md) for version history and updates.

---

**Made with ❤️ for algorithmic traders**

**Star ⭐ this repo if you find it useful!**

