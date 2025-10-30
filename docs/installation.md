# MyMT5 Installation Guide

Complete installation instructions for MyMT5 MetaTrader 5 Python trading system.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Install Prerequisites](#install-prerequisites)
3. [Install MyMT5](#install-mymt5)
4. [Configuration](#configuration)
5. [Verification](#verification)
6. [Troubleshooting](#troubleshooting)
7. [Platform-Specific Notes](#platform-specific-notes)

---

## System Requirements

### Operating System

- **Windows 10/11** (Recommended)
- **Linux** (Ubuntu 20.04+, Debian 10+, etc.) with Wine
- **macOS** (10.15+) with Wine or Virtual Machine

### Software Requirements

- **Python 3.8+** (Python 3.10+ recommended)
- **MetaTrader 5 Terminal** (latest version)
- **pip** (Python package installer)
- **Virtual environment** (recommended)

### Hardware Requirements (Minimum)

- **CPU**: Dual-core processor
- **RAM**: 4 GB
- **Storage**: 2 GB free space
- **Internet**: Stable broadband connection

### Hardware Requirements (Recommended)

- **CPU**: Quad-core processor or better
- **RAM**: 8 GB or more
- **Storage**: 10 GB free space (for data storage)
- **Internet**: High-speed broadband connection

---

## Install Prerequisites

### Step 1: Install Python

#### Windows

1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run the installer
3. **Important**: Check "Add Python to PATH"
4. Click "Install Now"

Verify installation:
```bash
python --version
# Should output: Python 3.x.x
```

#### Linux

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Fedora/RHEL
sudo dnf install python3 python3-pip

# Arch Linux
sudo pacman -S python python-pip
```

Verify installation:
```bash
python3 --version
pip3 --version
```

#### macOS

```bash
# Using Homebrew (recommended)
brew install python3

# Or download from python.org
```

Verify installation:
```bash
python3 --version
```

### Step 2: Install MetaTrader 5

#### Windows

1. Download MT5 from your broker's website
2. Run the installer (`mt5setup.exe`)
3. Follow installation wizard
4. Note the installation path (usually `C:\Program Files\MetaTrader 5\`)

#### Linux

MT5 on Linux requires Wine:

```bash
# Install Wine
sudo dpkg --add-architecture i386
sudo apt update
sudo apt install wine64 wine32 winetricks

# Download MT5 installer
wget https://download.mql5.com/cdn/web/metaquotes.software.corp/mt5/mt5setup.exe

# Run installer
wine mt5setup.exe
```

#### macOS

MT5 on macOS requires Wine or a Virtual Machine:

**Option 1: Using Wine (via Homebrew)**
```bash
# Install Wine
brew install --cask wine-stable

# Download and run MT5 installer
wine mt5setup.exe
```

**Option 2: Using Virtual Machine**
- Install VMware Fusion or Parallels Desktop
- Create Windows 10/11 virtual machine
- Install MT5 in the VM

### Step 3: Set Up MT5 Account

1. Open MetaTrader 5
2. Sign up for a demo account or use your live account
3. Note your credentials:
   - Login (account number)
   - Password
   - Server name

---

## Install MyMT5

### Option 1: Install from Source (Development)

```bash
# 1. Clone or download the repository
git clone https://github.com/yourusername/mymt5.git
cd mymt5

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 4. Install in editable mode
pip install -e .

# 5. Verify installation
python -c "from mymt5 import MT5Client; print('Success!')"
```

### Option 2: Install from Package (Production)

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 3. Install package
pip install mymt5

# 4. Verify installation
python -c "from mymt5 import MT5Client; print('Success!')"
```

### Option 3: Install from Requirements File

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/macOS

# 3. Install from requirements
pip install -r requirements.txt

# 4. If installing from source
pip install -e .
```

### Install Development Tools (Optional)

For contributors and developers:

```bash
# Install development dependencies
pip install pytest pytest-cov black flake8 mypy sphinx

# Or use dev requirements
pip install -r requirements-dev.txt
```

---

## Configuration

### Option 1: Configuration File (Recommended)

Create `config.ini` in your project directory:

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

[LOGGING]
level=INFO
file=logs/app.log
```

**Security**: Add `config.ini` to `.gitignore`!

```bash
# Create .gitignore if it doesn't exist
echo "config.ini" >> .gitignore
echo "*.log" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
```

### Option 2: Environment Variables

```bash
# Windows PowerShell
$env:MT5_LOGIN="12345678"
$env:MT5_PASSWORD="YourPassword"
$env:MT5_SERVER="YourBroker-Demo"
$env:MT5_PATH="C:\Program Files\MetaTrader 5\terminal64.exe"

# Linux/macOS (add to ~/.bashrc or ~/.zshrc)
export MT5_LOGIN="12345678"
export MT5_PASSWORD="YourPassword"
export MT5_SERVER="YourBroker-Demo"
export MT5_PATH="/path/to/mt5/terminal64.exe"
```

### Option 3: Python Configuration

```python
# config.py
MT5_CONFIG = {
    'login': 12345678,
    'password': 'YourPassword',
    'server': 'YourBroker-Demo',
    'path': r'C:\Program Files\MetaTrader 5\terminal64.exe',
    'timeout': 60000
}
```

### Create Project Structure

```bash
# Create directories
mkdir -p logs data/cache data/history examples

# Create example config
cat > config.ini.example << 'EOF'
[MT5]
login=YOUR_LOGIN
password=YOUR_PASSWORD
server=YOUR_SERVER
path=C:\Program Files\MetaTrader 5\terminal64.exe
timeout=60000
EOF

# Copy and edit
cp config.ini.example config.ini
# Edit config.ini with your credentials
```

---

## Verification

### Test 1: Import Test

```python
python -c "from mymt5 import MT5Client, MT5Account, MT5Symbol, MT5Trade; print('Imports successful!')"
```

Expected output: `Imports successful!`

### Test 2: Connection Test

Create `test_connection.py`:

```python
from mymt5 import MT5Client
import configparser

# Load config
config = configparser.ConfigParser()
config.read('config.ini')

# Create client
client = MT5Client()

# Initialize
success = client.initialize(
    login=int(config['MT5']['login']),
    password=config['MT5']['password'],
    server=config['MT5']['server']
)

if success:
    print("✓ Connection successful!")
    print(f"  State: {client.connection_state}")
    print(f"  Server: {client.account_server}")
else:
    print("✗ Connection failed!")
    error = client.get_error()
    print(f"  Error: {error}")

# Cleanup
client.shutdown()
```

Run test:
```bash
python test_connection.py
```

Expected output:
```
✓ Connection successful!
  State: ConnectionState.CONNECTED
  Server: YourBroker-Demo
```

### Test 3: Account Info Test

```python
from mymt5 import MT5Client, MT5Account
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

client = MT5Client()
client.initialize(
    login=int(config['MT5']['login']),
    password=config['MT5']['password'],
    server=config['MT5']['server']
)

if client.is_connected():
    account = MT5Account(client)
    balance = account.get('balance')
    equity = account.get('equity')
    
    print(f"✓ Account Info:")
    print(f"  Balance: ${balance}")
    print(f"  Equity: ${equity}")
else:
    print("✗ Not connected")

client.shutdown()
```

### Test 4: Run Example Scripts

```bash
# Run basic examples
python examples/01_basic_connection.py
python examples/02_account_info.py
python examples/03_market_data.py
```

### Test 5: Run Test Suite (For Developers)

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=mymt5 --cov-report=html

# Run specific test file
pytest tests/test_client.py -v
```

---

## Troubleshooting

### Issue: "Module 'MetaTrader5' not found"

**Solution**:
```bash
pip install MetaTrader5
```

### Issue: "Module 'mymt5' not found"

**Solution**:
```bash
# If installing from source
pip install -e .

# If using package
pip install mymt5

# Verify Python path
python -c "import sys; print(sys.path)"
```

### Issue: "Failed to initialize MT5"

**Possible causes and solutions**:

1. **MT5 not installed**
   ```bash
   # Verify MT5 installation
   # Windows: Check C:\Program Files\MetaTrader 5\
   ```

2. **Wrong MT5 path**
   ```python
   # Update path in config.ini
   path=C:\Program Files\MetaTrader 5\terminal64.exe
   ```

3. **MT5 already running**
   - Close all MT5 terminals
   - Try again

4. **Incorrect credentials**
   - Verify login, password, server
   - Check caps lock, typos

5. **Firewall blocking**
   - Allow MT5 in firewall
   - Check antivirus settings

### Issue: "Connection failed"

**Solution**:
```python
# Enable logging for diagnostics
import logging
logging.basicConfig(level=logging.DEBUG)

# Check error details
client = MT5Client()
success = client.initialize(...)
if not success:
    error = client.get_error()
    print(f"Error: {error}")
```

### Issue: "Symbol not found"

**Solution**:
```python
# Initialize symbol first
from mymt5 import MT5Symbol

symbol = MT5Symbol(client)
symbol.initialize('EURUSD')

# Verify symbol exists
exists = symbol.check('EURUSD', 'exists')
print(f"Symbol exists: {exists}")
```

### Issue: Virtual environment issues

**Solution**:
```bash
# Recreate virtual environment
deactivate  # If activated
rm -rf venv  # Remove old venv
python -m venv venv  # Create new
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/macOS
pip install -e .  # Reinstall
```

### Issue: Permission errors

**Solution**:
```bash
# Windows: Run terminal as Administrator
# Linux/macOS: Check file permissions
chmod +x scripts/*.py
```

### Getting Help

1. Check [Troubleshooting Guide](troubleshooting.md)
2. Review [examples/](../examples/)
3. Check [GitHub Issues](https://github.com/yourusername/mymt5/issues)
4. Read [User Guide](user_guide.md)

---

## Platform-Specific Notes

### Windows

- **Recommended platform** for MT5
- MT5 runs natively
- Use PowerShell or CMD
- Virtual environment: `venv\Scripts\activate`

### Linux

- MT5 requires Wine
- May have display issues (use Xvfb for headless)
- Virtual environment: `source venv/bin/activate`
- Some broker servers may not work with Wine

**Headless MT5 on Linux**:
```bash
# Install Xvfb
sudo apt install xvfb

# Run MT5 in virtual display
xvfb-run wine ~/.wine/drive_c/Program\ Files/MetaTrader\ 5/terminal64.exe
```

### macOS

- MT5 requires Wine or Virtual Machine
- Wine on Apple Silicon (M1/M2) can be problematic
- Consider using Virtual Machine for stability
- Virtual environment: `source venv/bin/activate`

---

## Post-Installation

### 1. Explore Examples

```bash
cd examples
ls -la
```

### 2. Read Documentation

- [Quick Start Guide](quickstart.md)
- [User Guide](user_guide.md)
- [API Reference](api_reference.md)

### 3. Configure Risk Management

Edit `config.ini`:
```ini
[RISK]
max_risk_per_trade=2.0
max_daily_loss=500.0
max_positions=5
max_symbol_positions=2
```

### 4. Set Up Logging

Create log directories:
```bash
mkdir -p logs
```

Configure logging in your code:
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
```

### 5. Create Backup of Configuration

```bash
cp config.ini config.ini.backup
```

---

## Updating MyMT5

### Update from Git

```bash
cd mymt5
git pull origin main
pip install -e . --upgrade
```

### Update from Package

```bash
pip install --upgrade mymt5
```

### Check Version

```python
import mymt5
print(mymt5.__version__)
```

---

## Uninstallation

```bash
# Uninstall package
pip uninstall mymt5

# Remove virtual environment
deactivate
rm -rf venv

# Remove configuration (optional)
rm config.ini

# Remove logs and data (optional)
rm -rf logs/ data/
```

---

## Next Steps

1. ✅ Complete [Quick Start Guide](quickstart.md)
2. ✅ Run example scripts in `examples/`
3. ✅ Read [User Guide](user_guide.md)
4. ✅ Build your first trading strategy

---

**Installation Complete!** You're ready to start trading with MyMT5! 🚀

For questions, see [Troubleshooting](troubleshooting.md) or [User Guide](user_guide.md).

