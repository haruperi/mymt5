# MT5 Trading System - Complete Project Structure

## 📁 Full Directory Tree

```
mt5_trading_system/
│
├── 📁 mymt5/                               # Source code (main package)
│   ├── __init__.py                        # Package initialization & exports
│   ├── client.py                          # MT5Client class
│   ├── account.py                         # MT5Account class
│   ├── symbol.py                          # MT5Symbol class
│   ├── data.py                            # MT5Data class
│   ├── trade.py                           # MT5Trade class
│   ├── history.py                         # MT5History class
│   ├── risk.py                            # MT5Risk class
│   ├── terminal.py                        # MT5Terminal class
│   ├── validator.py                       # MT5Validator class
│   ├── utils.py                           # MT5Utils class (static methods)
│   └── enums.py                           # Enumerations (ConnectionState, OrderType, TimeFrame)
│
├── 📁 tests/                               # Test suite
│   ├── __init__.py                        # Test package initialization
│   ├── conftest.py                        # pytest configuration & fixtures
│   ├── test_client.py                     # Tests for MT5Client
│   ├── test_account.py                    # Tests for MT5Account
│   ├── test_symbol.py                     # Tests for MT5Symbol
│   ├── test_data.py                       # Tests for MT5Data
│   ├── test_trade.py                      # Tests for MT5Trade
│   ├── test_history.py                    # Tests for MT5History
│   ├── test_risk.py                       # Tests for MT5Risk
│   ├── test_terminal.py                   # Tests for MT5Terminal
│   ├── test_validator.py                  # Tests for MT5Validator
│   ├── test_utils.py                      # Tests for MT5Utils
│   ├── test_integration.py                # Integration tests
│   └── test_end_to_end.py                 # End-to-end workflow tests
│
├── 📁 config/                              # Configuration files
│   ├── config.json                        # Main configuration (DO NOT COMMIT)
│   ├── config.example.json                # Configuration template
│   ├── config.dev.json                    # Development environment config
│   ├── config.prod.json                   # Production environment config
│   └── logging.conf                       # Logging configuration
│
├── 📁 logs/                                # Log files (auto-generated)
│   ├── mt5_system.log                     # Main application log
│   ├── trades.log                         # Trade execution log
│   ├── errors.log                         # Error log
│   └── connections.log                    # Connection events log
│
├── 📁 data/                                # Data storage
│   ├── cache/                             # Cached market data
│   │   ├── bars/                          # Cached OHLCV bars
│   │   └── ticks/                         # Cached tick data
│   ├── history/                           # Historical trade data
│   │   ├── deals/                         # Deal history exports
│   │   └── orders/                        # Order history exports
│   └── reports/                           # Generated reports
│       ├── performance/                   # Performance reports
│       └── risk/                          # Risk reports
│
├── 📁 docs/                                # Documentation
│   ├── architecture.md                    # System architecture documentation
│   ├── api_reference.md                   # API reference (auto-generated)
│   ├── user_guide.md                      # User guide
│   ├── installation.md                    # Installation instructions
│   ├── configuration.md                   # Configuration guide
│   ├── troubleshooting.md                 # Troubleshooting guide
│   ├── changelog.md                       # Version changelog
│   └── contributing.md                    # Contribution guidelines
│
├── 📁 examples/                            # Usage examples
│   ├── 01_basic_connection.py             # Basic connection example
│   ├── 02_account_info.py                 # Account information example
│   ├── 03_market_data.py                  # Market data retrieval example
│   ├── 04_simple_trade.py                 # Simple trading example
│   ├── 05_risk_management.py              # Risk management example
│   ├── 06_multi_symbol.py                 # Multi-symbol trading example
│   ├── 07_streaming_data.py               # Real-time data streaming example
│   ├── 08_historical_analysis.py          # Historical analysis example
│   ├── 09_strategy_template.py            # Strategy template example
│   └── 10_advanced_trading.py             # Advanced trading example
│
├── 📁 scripts/                             # Utility scripts
│   ├── setup_database.py                  # Database setup script
│   ├── export_data.py                     # Data export utility
│   ├── generate_report.py                 # Report generation script
│   ├── backup.py                          # Backup utility
│   └── migrate.py                         # Migration script
│
├── 📁 strategies/                          # Trading strategies (optional)
│   ├── __init__.py                        # Strategies package
│   ├── base_strategy.py                   # Base strategy class
│   ├── moving_average.py                  # Moving average strategy
│   ├── breakout.py                        # Breakout strategy
│   └── risk_management_rules.py           # Risk management rules
│
├── 📁 .github/                             # GitHub specific (optional)
│   ├── workflows/                         # CI/CD workflows
│   │   ├── tests.yml                      # Automated testing workflow
│   │   └── release.yml                    # Release workflow
│   ├── ISSUE_TEMPLATE/                    # Issue templates
│   │   ├── bug_report.md                  # Bug report template
│   │   └── feature_request.md             # Feature request template
│   └── PULL_REQUEST_TEMPLATE.md           # PR template
│
├── 📄 requirements.txt                     # Python dependencies
├── 📄 requirements-dev.txt                 # Development dependencies
├── 📄 setup.py                             # Package setup configuration
├── 📄 pyproject.toml                       # Modern Python project config
├── 📄 MANIFEST.in                          # Package manifest
├── 📄 pytest.ini                           # pytest configuration
├── 📄 .coveragerc                          # Coverage configuration
├── 📄 .flake8                              # Flake8 linting configuration
├── 📄 .pre-commit-config.yaml              # Pre-commit hooks
├── 📄 mypy.ini                             # Type checking configuration
├── 📄 .gitignore                           # Git ignore rules
├── 📄 .env                                 # Environment variables (DO NOT COMMIT)
├── 📄 .env.example                         # Environment variables template
├── 📄 README.md                            # Project README
├── 📄 LICENSE                              # License file
├── 📄 CHANGELOG.md                         # Version changelog
└── 📄 TODO.md                              # TODO list
```

---

## 📊 Structure Breakdown by Category

### 1. Core Source Code (`mymt5/`)
**Purpose**: Main application code
**Files**: 12 Python files (~120 methods total)

```
mymt5/
├── Core Layer
│   └── client.py              (MT5Client - ~25 methods)
│
├── Information Layer
│   ├── account.py             (MT5Account - ~10 methods)
│   ├── symbol.py              (MT5Symbol - ~15 methods)
│   └── terminal.py            (MT5Terminal - ~8 methods)
│
├── Data Layer
│   ├── data.py                (MT5Data - ~15 methods)
│   └── history.py             (MT5History - ~12 methods)
│
├── Trading Layer
│   ├── trade.py               (MT5Trade - ~18 methods)
│   └── risk.py                (MT5Risk - ~12 methods)
│
├── Utility Layer
│   ├── validator.py           (MT5Validator - ~5 methods)
│   └── utils.py               (MT5Utils - ~12 static methods)
│
└── Foundation
    ├── enums.py               (3 enumerations)
    └── __init__.py            (Package exports)
```

### 2. Tests (`tests/`)
**Purpose**: Comprehensive test suite
**Coverage Goal**: 80%+

```
tests/
├── Unit Tests (per class)
│   ├── test_client.py         (~20 test functions)
│   ├── test_account.py        (~10 test functions)
│   ├── test_symbol.py         (~15 test functions)
│   ├── test_data.py           (~15 test functions)
│   ├── test_trade.py          (~18 test functions)
│   ├── test_history.py        (~12 test functions)
│   ├── test_risk.py           (~12 test functions)
│   ├── test_terminal.py       (~8 test functions)
│   ├── test_validator.py      (~10 test functions)
│   └── test_utils.py          (~12 test functions)
│
├── Integration Tests
│   └── test_integration.py    (Cross-class interactions)
│
├── End-to-End Tests
│   └── test_end_to_end.py     (Complete workflows)
│
└── Configuration
    └── conftest.py            (Fixtures & setup)
```

### 3. Configuration (`config/`)
**Purpose**: Environment and runtime configuration

```
config/
├── config.json                # Active config (gitignored)
├── config.example.json        # Template for users
├── config.dev.json            # Development settings
├── config.prod.json           # Production settings
└── logging.conf               # Logging configuration

Configuration Structure:
{
  "connection": {...},         # MT5 connection settings
  "accounts": {...},           # Account credentials
  "risk": {...},              # Risk management settings
  "logging": {...},           # Logging configuration
  "cache": {...},             # Cache settings
  "features": {...}           # Feature flags
}
```

### 4. Logs (`logs/`)
**Purpose**: Application logging (auto-generated)

```
logs/
├── mt5_system.log             # Main application log
├── trades.log                 # Trade execution log
├── errors.log                 # Error-only log
├── connections.log            # Connection events
├── performance.log            # Performance metrics
└── archive/                   # Log archives
    ├── mt5_system_2024-01.log.gz
    └── mt5_system_2024-02.log.gz
```

### 5. Data Storage (`data/`)
**Purpose**: Cached data and reports

```
data/
├── cache/                     # Cached market data
│   ├── bars/
│   │   ├── EURUSD_H1.parquet
│   │   ├── GBPUSD_H1.parquet
│   │   └── ...
│   └── ticks/
│       ├── EURUSD_ticks.parquet
│       └── ...
│
├── history/                   # Historical exports
│   ├── deals/
│   │   ├── deals_2024-01.csv
│   │   └── deals_2024-02.csv
│   └── orders/
│       ├── orders_2024-01.csv
│       └── orders_2024-02.csv
│
└── reports/                   # Generated reports
    ├── performance/
    │   ├── monthly_2024-01.pdf
    │   └── monthly_2024-02.pdf
    └── risk/
        ├── risk_analysis_2024-01.pdf
        └── risk_analysis_2024-02.pdf
```

### 6. Documentation (`docs/`)
**Purpose**: Project documentation

```
docs/
├── architecture.md            # System architecture
├── api_reference.md           # API documentation
├── user_guide.md              # User guide
├── installation.md            # Installation steps
├── configuration.md           # Configuration guide
├── troubleshooting.md         # Common issues
├── changelog.md               # Version history
├── contributing.md            # Contribution guidelines
├── images/                    # Documentation images
│   ├── architecture_diagram.png
│   ├── class_diagram.png
│   └── workflow.png
└── diagrams/                  # Source diagrams
    ├── architecture.mermaid
    └── class_diagram.mermaid
```

### 7. Examples (`examples/`)
**Purpose**: Usage examples and templates

```
examples/
├── Beginner Level
│   ├── 01_basic_connection.py
│   ├── 02_account_info.py
│   └── 03_market_data.py
│
├── Intermediate Level
│   ├── 04_simple_trade.py
│   ├── 05_risk_management.py
│   └── 06_multi_symbol.py
│
└── Advanced Level
    ├── 07_streaming_data.py
    ├── 08_historical_analysis.py
    ├── 09_strategy_template.py
    └── 10_advanced_trading.py
```

### 8. Scripts (`scripts/`)
**Purpose**: Utility and maintenance scripts

```
scripts/
├── setup_database.py          # Initialize database
├── export_data.py             # Export historical data
├── generate_report.py         # Generate reports
├── backup.py                  # Backup data
├── migrate.py                 # Database migrations
├── cleanup.py                 # Cleanup old data
└── monitor.py                 # System monitoring
```

### 9. Configuration Files (Root)
**Purpose**: Development and build configuration

```
Root Level:
├── requirements.txt           # Production dependencies
├── requirements-dev.txt       # Development dependencies
├── setup.py                   # Package setup
├── pyproject.toml             # Modern Python config
├── MANIFEST.in                # Package files
├── pytest.ini                 # pytest settings
├── .coveragerc                # Coverage settings
├── .flake8                    # Linting rules
├── mypy.ini                   # Type checking
├── .pre-commit-config.yaml    # Git hooks
├── .gitignore                 # Git ignore
├── .env.example               # Environment template
├── README.md                  # Project overview
├── LICENSE                    # License
├── CHANGELOG.md               # Version history
└── TODO.md                    # Task list
```

---

## 📦 Package Structure (After Installation)

When installed as a package:

```python
import mt5_trading_system

# Available classes
from mt5_trading_system import (
    MT5Client,
    MT5Account,
    MT5Symbol,
    MT5Data,
    MT5Trade,
    MT5History,
    MT5Risk,
    MT5Terminal,
    MT5Validator,
    MT5Utils,
    ConnectionState,
    OrderType,
    TimeFrame
)
```

---

## 🔧 File Sizes (Estimated)

```
Source Code (mymt5/):
├── client.py           ~800 lines   ~30 KB
├── account.py          ~300 lines   ~12 KB
├── symbol.py           ~500 lines   ~20 KB
├── data.py             ~600 lines   ~25 KB
├── trade.py            ~700 lines   ~28 KB
├── history.py          ~450 lines   ~18 KB
├── risk.py             ~450 lines   ~18 KB
├── terminal.py         ~250 lines   ~10 KB
├── validator.py        ~400 lines   ~15 KB
├── utils.py            ~500 lines   ~20 KB
├── enums.py            ~100 lines   ~4 KB
└── __init__.py         ~50 lines    ~2 KB
Total:                  ~5,100 lines ~202 KB

Tests (tests/):
Total:                  ~3,000 lines ~120 KB

Documentation (docs/):
Total:                  ~50 pages    ~200 KB

Total Project Size:     ~8,000+ lines ~500+ KB
```

---

## 🎯 Key Directories Explained

### `/src` - Source Code
- **What**: All production code
- **When to modify**: During development
- **Commit**: Yes
- **Backup**: Yes

### `/tests` - Test Suite  
- **What**: All test files
- **When to modify**: Alongside feature development
- **Commit**: Yes
- **Backup**: Yes

### `/config` - Configuration
- **What**: Settings and credentials
- **When to modify**: Setup and deployment
- **Commit**: Only templates (*.example.json)
- **Backup**: Yes (encrypted)

### `/logs` - Log Files
- **What**: Application logs
- **When to modify**: Never (auto-generated)
- **Commit**: No
- **Backup**: Optional (for debugging)

### `/data` - Data Storage
- **What**: Cached data and reports
- **When to modify**: Never (auto-generated)
- **Commit**: No
- **Backup**: Optional

### `/docs` - Documentation
- **What**: Project documentation
- **When to modify**: When features change
- **Commit**: Yes
- **Backup**: Yes

### `/examples` - Usage Examples
- **What**: Example scripts
- **When to modify**: When adding features
- **Commit**: Yes
- **Backup**: Yes

### `/scripts` - Utility Scripts
- **What**: Maintenance and utility scripts
- **When to modify**: As needed
- **Commit**: Yes
- **Backup**: Yes

---

## 🚀 Quick Setup Commands

### Create Structure Automatically
```bash
# Run the setup script
python setup_project.py

# Or manually create structure
mkdir -p mt5_trading_system/{src,tests,config,logs,data/{cache/{bars,ticks},history/{deals,orders},reports/{performance,risk}},docs,examples,scripts}
```

### Initialize Git
```bash
cd mt5_trading_system
git init
git add .
git commit -m "Initial project structure"
```

### Setup Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## 📋 Gitignore Configuration

Essential files to ignore:

```gitignore
# Credentials and Config
config/config.json
.env

# Logs
logs/
*.log

# Data
data/cache/
data/history/
data/reports/

# Python
__pycache__/
*.pyc
*.pyo
*.egg-info/
dist/
build/

# Virtual Environment
venv/
env/

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db
```

---

## 🔍 File Search Quick Reference

### Find Python Files
```bash
find . -name "*.py" -type f
```

### Find Test Files
```bash
find tests/ -name "test_*.py"
```

### Count Lines of Code
```bash
find mymt5/ -name "*.py" -exec wc -l {} + | tail -1
```

### List Large Files
```bash
find . -type f -size +1M
```

---

## 📊 Development Workflow

### Daily Development
```
1. Work in: /src
2. Write tests in: /tests
3. Run tests: pytest
4. Check logs: /logs
5. Commit changes: git
```

### Configuration Changes
```
1. Modify: /config/config.json
2. Test changes
3. Update: /config/config.example.json (if needed)
4. Document: /docs/configuration.md
```

### Adding Features
```
1. Update: /src files
2. Add tests: /tests
3. Create example: /examples
4. Document: /docs
5. Update: CHANGELOG.md
```

---

## ✅ Structure Validation Checklist

After setup, verify:

```
✓ /src contains all 12 Python files
✓ /tests contains all test files
✓ /config has example templates
✓ /logs directory exists (may be empty)
✓ /data directories exist
✓ /docs has architecture.md
✓ /examples has basic examples
✓ requirements.txt exists
✓ setup.py configured
✓ .gitignore present
✓ README.md complete
✓ Virtual environment created
✓ Dependencies installed
```

---

## 🎯 Directory Access Patterns

### For Developers
```
Primary: /src, /tests
Secondary: /examples, /docs
Occasional: /scripts, /config
```

### For Users
```
Primary: /examples
Secondary: /docs, /config
Never: /src (unless customizing)
```

### For CI/CD
```
Primary: /tests, /src
Secondary: /scripts
Output: /logs, /data/reports
```

---

This structure provides:
- ✅ Clear separation of concerns
- ✅ Easy navigation
- ✅ Scalable organization
- ✅ Professional layout
- ✅ Testing-friendly structure
- ✅ Documentation-ready
- ✅ Git-friendly
- ✅ Production-ready

**Total Estimated Size**: ~500+ KB  
**Total Files**: 50+ files  
**Lines of Code**: 8,000+ lines
