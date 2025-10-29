"""
MT5 Trading System - Enumerations Module

This module contains all enumeration classes used throughout the MT5 trading system.
These enums provide type-safe constants for connection states, order types, and timeframes.
"""

from mylogger import logger
from enum import Enum, IntEnum
import MetaTrader5 as mt5


logger.info("Loading enums module")


class ConnectionState(Enum):
    """
    Enumeration representing the connection state to MT5 terminal.

    Attributes:
        DISCONNECTED: Not connected to MT5 terminal
        CONNECTED: Successfully connected to MT5 terminal
        FAILED: Connection attempt failed
        INITIALIZING: Connection is being initialized
        RECONNECTING: Attempting to reconnect to MT5 terminal
    """
    DISCONNECTED = "disconnected"
    CONNECTED = "connected"
    FAILED = "failed"
    INITIALIZING = "initializing"
    RECONNECTING = "reconnecting"

    def __str__(self) -> str:
        """Return string representation of the connection state."""
        return self.value

    def __repr__(self) -> str:
        """Return detailed representation of the connection state."""
        return f"ConnectionState.{self.name}"


class OrderType(IntEnum):
    """
    Enumeration representing MT5 order types.

    Maps to MetaTrader5 order type constants for compatibility.

    Attributes:
        BUY: Market buy order
        SELL: Market sell order
        BUY_LIMIT: Buy limit pending order
        SELL_LIMIT: Sell limit pending order
        BUY_STOP: Buy stop pending order
        SELL_STOP: Sell stop pending order
        BUY_STOP_LIMIT: Buy stop limit pending order
        SELL_STOP_LIMIT: Sell stop limit pending order
    """
    BUY = mt5.ORDER_TYPE_BUY
    SELL = mt5.ORDER_TYPE_SELL
    BUY_LIMIT = mt5.ORDER_TYPE_BUY_LIMIT
    SELL_LIMIT = mt5.ORDER_TYPE_SELL_LIMIT
    BUY_STOP = mt5.ORDER_TYPE_BUY_STOP
    SELL_STOP = mt5.ORDER_TYPE_SELL_STOP
    BUY_STOP_LIMIT = mt5.ORDER_TYPE_BUY_STOP_LIMIT
    SELL_STOP_LIMIT = mt5.ORDER_TYPE_SELL_STOP_LIMIT

    def __str__(self) -> str:
        """Return string representation of the order type."""
        return self.name

    def __repr__(self) -> str:
        """Return detailed representation of the order type."""
        return f"OrderType.{self.name}"

    @classmethod
    def is_market_order(cls, order_type: 'OrderType') -> bool:
        """
        Check if the order type is a market order.

        Args:
            order_type: The order type to check

        Returns:
            True if the order type is BUY or SELL, False otherwise
        """
        return order_type in (cls.BUY, cls.SELL)

    @classmethod
    def is_pending_order(cls, order_type: 'OrderType') -> bool:
        """
        Check if the order type is a pending order.

        Args:
            order_type: The order type to check

        Returns:
            True if the order type is a pending order, False otherwise
        """
        return not cls.is_market_order(order_type)

    @classmethod
    def is_buy_order(cls, order_type: 'OrderType') -> bool:
        """
        Check if the order type is a buy order.

        Args:
            order_type: The order type to check

        Returns:
            True if the order type is a buy variant, False otherwise
        """
        return order_type in (cls.BUY, cls.BUY_LIMIT, cls.BUY_STOP, cls.BUY_STOP_LIMIT)

    @classmethod
    def is_sell_order(cls, order_type: 'OrderType') -> bool:
        """
        Check if the order type is a sell order.

        Args:
            order_type: The order type to check

        Returns:
            True if the order type is a sell variant, False otherwise
        """
        return order_type in (cls.SELL, cls.SELL_LIMIT, cls.SELL_STOP, cls.SELL_STOP_LIMIT)


class TimeFrame(IntEnum):
    """
    Enumeration representing MT5 timeframes.

    Maps to MetaTrader5 timeframe constants for compatibility.

    Attributes:
        M1: 1 minute timeframe
        M5: 5 minutes timeframe
        M15: 15 minutes timeframe
        M30: 30 minutes timeframe
        H1: 1 hour timeframe
        H4: 4 hours timeframe
        D1: 1 day timeframe
        W1: 1 week timeframe
        MN1: 1 month timeframe
    """
    M1 = mt5.TIMEFRAME_M1
    M5 = mt5.TIMEFRAME_M5
    M15 = mt5.TIMEFRAME_M15
    M30 = mt5.TIMEFRAME_M30
    H1 = mt5.TIMEFRAME_H1
    H4 = mt5.TIMEFRAME_H4
    D1 = mt5.TIMEFRAME_D1
    W1 = mt5.TIMEFRAME_W1
    MN1 = mt5.TIMEFRAME_MN1

    def __str__(self) -> str:
        """Return string representation of the timeframe."""
        return self.name

    def __repr__(self) -> str:
        """Return detailed representation of the timeframe."""
        return f"TimeFrame.{self.name}"

    @property
    def minutes(self) -> int:
        """
        Get the timeframe duration in minutes.

        Returns:
            Number of minutes in the timeframe
        """
        timeframe_minutes = {
            self.M1: 1,
            self.M5: 5,
            self.M15: 15,
            self.M30: 30,
            self.H1: 60,
            self.H4: 240,
            self.D1: 1440,
            self.W1: 10080,
            self.MN1: 43200  # Approximate: 30 days * 24 hours * 60 minutes
        }
        return timeframe_minutes.get(self, 0)

    @classmethod
    def from_string(cls, timeframe_str: str) -> 'TimeFrame':
        """
        Convert a string representation to a TimeFrame enum.

        Args:
            timeframe_str: String representation of timeframe (e.g., 'M1', 'H1', 'D1')

        Returns:
            TimeFrame enum value

        Raises:
            ValueError: If the string doesn't match any timeframe
        """
        timeframe_str = timeframe_str.upper()
        try:
            return cls[timeframe_str]
        except KeyError:
            raise ValueError(f"Invalid timeframe string: {timeframe_str}")

    @classmethod
    def from_minutes(cls, minutes: int) -> 'TimeFrame':
        """
        Get the closest matching timeframe from minutes.

        Args:
            minutes: Number of minutes

        Returns:
            TimeFrame enum value

        Raises:
            ValueError: If no matching timeframe is found
        """
        minute_to_timeframe = {
            1: cls.M1,
            5: cls.M5,
            15: cls.M15,
            30: cls.M30,
            60: cls.H1,
            240: cls.H4,
            1440: cls.D1,
            10080: cls.W1,
            43200: cls.MN1
        }

        if minutes in minute_to_timeframe:
            return minute_to_timeframe[minutes]
        else:
            raise ValueError(f"No timeframe matches {minutes} minutes")


# Export all enums
__all__ = ['ConnectionState', 'OrderType', 'TimeFrame']
