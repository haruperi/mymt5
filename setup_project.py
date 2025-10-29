#!/usr/bin/env python3
"""
MT5 Trading System - Project Setup Script
This script creates the complete project structure for the MT5 trading system
"""

import os
import sys
from pathlib import Path


def create_directory(path):
    """Create directory if it doesn't exist"""
    Path(path).mkdir(parents=True, exist_ok=True)
    print(f"✓ Created directory: {path}")


def create_file(path, content=""):
    """Create file with optional content"""
    with open(path, 'w') as f:
        f.write(content)
    print(f"✓ Created file: {path}")


def setup_project():
    """Create the complete project structure"""
    
    print("\n" + "="*60)
    print("MT5 Trading System - Project Setup")
    print("="*60 + "\n")
    
    # Get project name
    project_name = input("Enter project name (default: mt5_trading_system): ").strip()
    if not project_name:
        project_name = "mt5_trading_system"
    
    print(f"\nCreating project: {project_name}\n")
    
    # Create root directory
    create_directory(project_name)
    os.chdir(project_name)
    
    # Create main directories
    directories = [
        "src",
        "tests",
        "config",
        "logs",
        "data",
        "docs",
        "examples"
    ]
    
    for directory in directories:
        create_directory(directory)
    
    # Create src files
    src_files = [
        "__init__.py",
        "client.py",
        "account.py",
        "symbol.py",
        "data.py",
        "trade.py",
        "history.py",
        "risk.py",
        "terminal.py",
        "validator.py",
        "utils.py",
        "enums.py"
    ]
    
    print("\nCreating source files...")
    for file in src_files:
        create_file(f"src/{file}", get_file_template(file))
    
    # Create test files
    test_files = [
        "__init__.py",
        "test_client.py",
        "test_account.py",
        "test_symbol.py",
        "test_data.py",
        "test_trade.py",
        "test_history.py",
        "test_risk.py",
        "test_terminal.py",
        "test_validator.py",
        "test_utils.py"
    ]
    
    print("\nCreating test files...")
    for file in test_files:
        create_file(f"tests/{file}", get_test_template(file))
    
    # Create configuration files
    print("\nCreating configuration files...")
    create_file("config/config.example.json", get_config_template())
    create_file("requirements.txt", get_requirements())
    create_file("setup.py", get_setup_py())
    create_file(".gitignore", get_gitignore())
    create_file("README.md", get_readme())
    create_file("pytest.ini", get_pytest_ini())
    create_file(".env.example", get_env_example())
    
    # Create example files
    print("\nCreating example files...")
    create_file("examples/basic_usage.py", get_basic_example())
    create_file("examples/trading_example.py", "# Trading example - to be implemented\n")
    create_file("examples/risk_management_example.py", "# Risk management example - to be implemented\n")
    
    # Create documentation
    print("\nCreating documentation...")
    create_file("docs/architecture.md", "# Architecture Documentation\n\nSee MT5_Architecture_Documentation.md for details.\n")
    create_file("docs/api_reference.md", "# API Reference\n\nTo be generated from docstrings.\n")
    
    print("\n" + "="*60)
    print("Project Setup Complete!")
    print("="*60)
    print(f"\nProject created at: {os.getcwd()}")
    print("\nNext steps:")
    print("1. cd", project_name)
    print("2. python -m venv venv")
    print("3. source venv/bin/activate  # On Windows: venv\\Scripts\\activate")
    print("4. pip install -r requirements.txt")
    print("5. Copy config/config.example.json to config/config.json")
    print("6. Update config/config.json with your MT5 credentials")
    print("7. Start implementing!")
    print("\n")


def get_file_template(filename):
    """Get template content for source files"""
    templates = {
        "__init__.py": '''"""MT5 Trading System"""

__version__ = "1.0.0"
__author__ = "Your Name"

from .client import MT5Client
from .account import MT5Account
from .symbol import MT5Symbol
from .data import MT5Data
from .trade import MT5Trade
from .history import MT5History
from .risk import MT5Risk
from .terminal import MT5Terminal
from .validator import MT5Validator
from .utils import MT5Utils
from .enums import ConnectionState, OrderType, TimeFrame

__all__ = [
    "MT5Client",
    "MT5Account",
    "MT5Symbol",
    "MT5Data",
    "MT5Trade",
    "MT5History",
    "MT5Risk",
    "MT5Terminal",
    "MT5Validator",
    "MT5Utils",
    "ConnectionState",
    "OrderType",
    "TimeFrame",
]
''',
        "enums.py": '''"""Enumerations for MT5 Trading System"""

from enum import Enum


class ConnectionState(Enum):
    """Connection state enumeration"""
    DISCONNECTED = 0
    CONNECTED = 1
    FAILED = 2
    INITIALIZING = 3
    RECONNECTING = 4


class OrderType(Enum):
    """Order type enumeration"""
    BUY = 'buy'
    SELL = 'sell'
    BUY_LIMIT = 'buy_limit'
    SELL_LIMIT = 'sell_limit'
    BUY_STOP = 'buy_stop'
    SELL_STOP = 'sell_stop'
    BUY_STOP_LIMIT = 'buy_stop_limit'
    SELL_STOP_LIMIT = 'sell_stop_limit'


class TimeFrame(Enum):
    """Timeframe enumeration"""
    M1 = 1
    M5 = 5
    M15 = 15
    M30 = 30
    H1 = 60
    H4 = 240
    D1 = 1440
    W1 = 10080
    MN1 = 43200
''',
        "client.py": '''"""MT5 Client - Core connection manager"""

import MetaTrader5 as mt5
import logging
from typing import Optional, Dict, Callable
from .enums import ConnectionState


class MT5Client:
    """
    Core MT5 connection manager
    
    Handles connection, authentication, and configuration for MT5 terminal.
    """
    
    def __init__(self, config_path: Optional[str] = None, auto_reconnect: bool = True):
        """
        Initialize MT5 Client
        
        Args:
            config_path: Path to configuration file
            auto_reconnect: Enable automatic reconnection
        """
        self.config = {}
        self.connection_state = ConnectionState.DISCONNECTED
        self.auto_reconnect = auto_reconnect
        self._callbacks = {}
        self._setup_logging()
        
        if config_path:
            self.load_config(config_path)
    
    def _setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def initialize(self, path: Optional[str] = None, 
                   timeout: int = 60000, 
                   portable: bool = False) -> bool:
        """
        Initialize MT5 terminal connection
        
        Args:
            path: Path to MT5 terminal
            timeout: Connection timeout in milliseconds
            portable: Use portable mode
            
        Returns:
            bool: True if successful
        """
        # TODO: Implement initialization
        pass
    
    def login(self, account: Optional[int] = None, 
              password: Optional[str] = None, 
              server: Optional[str] = None) -> bool:
        """
        Login to MT5 account
        
        Args:
            account: Account number
            password: Account password
            server: Server name
            
        Returns:
            bool: True if successful
        """
        # TODO: Implement login
        pass
    
    # TODO: Implement other methods
''',
    }
    
    return templates.get(filename, f'"""{filename}"""\n\n# TODO: Implement\npass\n')


def get_test_template(filename):
    """Get template for test files"""
    if filename == "__init__.py":
        return ""
    
    class_name = filename.replace("test_", "").replace(".py", "").title()
    return f'''"""Tests for {class_name}"""

import pytest
from src.{filename.replace("test_", "").replace(".py", "")} import *


class Test{class_name}:
    """Test suite for {class_name}"""
    
    def test_placeholder(self):
        """Placeholder test"""
        # TODO: Implement tests
        assert True
'''


def get_config_template():
    """Get configuration template"""
    return '''{
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
      "password": "your_password",
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
    "file": "logs/mt5_system.log",
    "max_size": 10485760,
    "backup_count": 5
  }
}
'''


def get_requirements():
    """Get requirements.txt content"""
    return '''# Core dependencies
MetaTrader5>=5.0.0
pandas>=1.3.0
numpy>=1.21.0
python-dateutil>=2.8.0

# Development dependencies
pytest>=7.0.0
pytest-cov>=3.0.0
black>=22.0.0
flake8>=4.0.0
mypy>=0.950
'''


def get_setup_py():
    """Get setup.py content"""
    return '''from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mt5-trading-system",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A comprehensive MetaTrader 5 Python trading system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/mt5-trading-system",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "MetaTrader5>=5.0.0",
        "pandas>=1.3.0",
        "numpy>=1.21.0",
        "python-dateutil>=2.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
    },
)
'''


def get_gitignore():
    """Get .gitignore content"""
    return '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# Logs
logs/
*.log

# Config
config/config.json
.env

# Data
data/
*.db
*.sqlite

# OS
.DS_Store
Thumbs.db
'''


def get_readme():
    """Get README.md content"""
    return '''# MT5 Trading System

A comprehensive Python trading system for MetaTrader 5.

## Features

- 🔌 Robust connection management with auto-reconnection
- 📊 Complete market data retrieval (OHLCV, ticks)
- 💰 Full trading capabilities (market & pending orders)
- 📈 Position and order management
- 🎯 Advanced risk management
- 📉 Historical data analysis
- ✅ Input validation
- 🔧 Extensive utilities

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/mt5-trading-system.git
cd mt5-trading-system
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure settings:
```bash
cp config/config.example.json config/config.json
# Edit config/config.json with your credentials
```

## Quick Start

```python
from src import MT5Client, MT5Account, MT5Trade

# Initialize client
client = MT5Client(config_path='config/config.json')
client.initialize()
client.login()

# Get account info
account = MT5Account(client)
balance = account.get('balance')
print(f"Balance: ${balance}")

# Execute trade
trade = MT5Trade(client, symbol_manager)
result = trade.buy('EURUSD', 0.1, sl=1.0900, tp=1.1100)
print(f"Order result: {result}")
```

## Documentation

See `docs/` directory for detailed documentation:
- Architecture overview
- API reference
- Usage examples

## Testing

Run tests:
```bash
pytest tests/ -v
```

Run with coverage:
```bash
pytest tests/ -v --cov=src --cov-report=html
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.

## Disclaimer

This software is for educational purposes only. Use at your own risk. 
The authors are not responsible for any financial losses incurred through 
the use of this software.
'''


def get_pytest_ini():
    """Get pytest.ini content"""
    return '''[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --strict-markers
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
'''


def get_env_example():
    """Get .env.example content"""
    return '''# MT5 Account Credentials
MT5_ACCOUNT=12345
MT5_PASSWORD=your_password
MT5_SERVER=Broker-Server

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/mt5_system.log
'''


def get_basic_example():
    """Get basic usage example"""
    return '''"""
Basic Usage Example for MT5 Trading System
"""

from src import MT5Client, MT5Account, MT5Symbol, MT5Data


def main():
    """Basic usage example"""
    
    # Initialize client
    print("Initializing MT5 client...")
    client = MT5Client(config_path='config/config.json', auto_reconnect=True)
    
    # Connect and login
    if not client.initialize():
        print("Failed to initialize")
        return
    
    if not client.login():
        print("Failed to login")
        return
    
    print("Connected successfully!")
    
    # Get account information
    account = MT5Account(client)
    balance = account.get('balance')
    equity = account.get('equity')
    print(f"\\nAccount Info:")
    print(f"Balance: ${balance:.2f}")
    print(f"Equity: ${equity:.2f}")
    
    # Initialize symbols
    symbol = MT5Symbol(client)
    symbol.initialize(['EURUSD', 'GBPUSD'])
    
    # Get current price
    price = symbol.get_price('EURUSD', 'bid')
    print(f"\\nEURUSD Bid: {price}")
    
    # Get historical data
    data = MT5Data(client)
    bars = data.get_bars('EURUSD', 'H1', count=10)
    print(f"\\nLast 10 H1 bars retrieved: {len(bars)} bars")
    
    # Cleanup
    client.shutdown()
    print("\\nDisconnected")


if __name__ == "__main__":
    main()
'''


if __name__ == "__main__":
    try:
        setup_project()
    except KeyboardInterrupt:
        print("\\n\\nSetup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\\n\\nError during setup: {e}")
        sys.exit(1)
