"""
MyMT5 - MetaTrader 5 Python Trading System

A comprehensive Python library for interacting with MetaTrader 5 terminal.

Example:
    >>> from mymt5 import MT5Client, MT5Account, MT5Trade
    >>> client = MT5Client()
    >>> client.initialize(login=12345, password='pass', server='server')
    >>> account = MT5Account(client)
    >>> balance = account.get('balance')
    >>> client.shutdown()
"""

from mymt5.__version__ import (
    __version__,
    __version_info__,
    __title__,
    __description__,
    __url__,
    __author__,
    __author_email__,
    __license__,
    __copyright__,
)

# Core imports
from mymt5.client import MT5Client
from mymt5.account import MT5Account
from mymt5.symbol import MT5Symbol
from mymt5.terminal import MT5Terminal
from mymt5.data import MT5Data
from mymt5.history import MT5History
from mymt5.trade import MT5Trade
from mymt5.risk import MT5Risk
from mymt5.validator import MT5Validator
from mymt5.utils import MT5Utils

# Enums
from mymt5.enums import ConnectionState, OrderType, TimeFrame

__all__ = [
    # Version info
    '__version__',
    '__version_info__',
    '__title__',
    '__description__',
    '__url__',
    '__author__',
    '__author_email__',
    '__license__',
    '__copyright__',
    
    # Core classes
    'MT5Client',
    'MT5Account',
    'MT5Symbol',
    'MT5Terminal',
    'MT5Data',
    'MT5History',
    'MT5Trade',
    'MT5Risk',
    'MT5Validator',
    'MT5Utils',
    
    # Enums
    'ConnectionState',
    'OrderType',
    'TimeFrame',
]
