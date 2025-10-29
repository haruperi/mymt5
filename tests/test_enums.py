"""
Unit tests for MT5 Trading System Enumerations

Tests all enum classes and their helper methods.
"""

import pytest
import MetaTrader5 as mt5
from mymt5.enums import ConnectionState, OrderType, TimeFrame


class TestConnectionState:
    """Test suite for ConnectionState enum."""

    def test_connection_state_values(self):
        """Test that all ConnectionState values are defined correctly."""
        assert ConnectionState.DISCONNECTED.value == "disconnected"
        assert ConnectionState.CONNECTED.value == "connected"
        assert ConnectionState.FAILED.value == "failed"
        assert ConnectionState.INITIALIZING.value == "initializing"
        assert ConnectionState.RECONNECTING.value == "reconnecting"

    def test_connection_state_count(self):
        """Test that all expected connection states are present."""
        expected_states = {'DISCONNECTED', 'CONNECTED', 'FAILED', 'INITIALIZING', 'RECONNECTING'}
        actual_states = {state.name for state in ConnectionState}
        assert actual_states == expected_states

    def test_connection_state_str(self):
        """Test string representation of ConnectionState."""
        assert str(ConnectionState.CONNECTED) == "connected"
        assert str(ConnectionState.DISCONNECTED) == "disconnected"
        assert str(ConnectionState.FAILED) == "failed"

    def test_connection_state_repr(self):
        """Test detailed representation of ConnectionState."""
        assert repr(ConnectionState.CONNECTED) == "ConnectionState.CONNECTED"
        assert repr(ConnectionState.FAILED) == "ConnectionState.FAILED"

    def test_connection_state_equality(self):
        """Test ConnectionState equality comparison."""
        state1 = ConnectionState.CONNECTED
        state2 = ConnectionState.CONNECTED
        state3 = ConnectionState.DISCONNECTED

        assert state1 == state2
        assert state1 != state3

    def test_connection_state_membership(self):
        """Test ConnectionState membership checks."""
        state = ConnectionState.CONNECTED
        assert state in ConnectionState
        assert state in [ConnectionState.CONNECTED, ConnectionState.DISCONNECTED]


class TestOrderType:
    """Test suite for OrderType enum."""

    def test_order_type_values(self):
        """Test that OrderType values match MT5 constants."""
        assert OrderType.BUY == mt5.ORDER_TYPE_BUY
        assert OrderType.SELL == mt5.ORDER_TYPE_SELL
        assert OrderType.BUY_LIMIT == mt5.ORDER_TYPE_BUY_LIMIT
        assert OrderType.SELL_LIMIT == mt5.ORDER_TYPE_SELL_LIMIT
        assert OrderType.BUY_STOP == mt5.ORDER_TYPE_BUY_STOP
        assert OrderType.SELL_STOP == mt5.ORDER_TYPE_SELL_STOP
        assert OrderType.BUY_STOP_LIMIT == mt5.ORDER_TYPE_BUY_STOP_LIMIT
        assert OrderType.SELL_STOP_LIMIT == mt5.ORDER_TYPE_SELL_STOP_LIMIT

    def test_order_type_count(self):
        """Test that all expected order types are present."""
        expected_types = {
            'BUY', 'SELL', 'BUY_LIMIT', 'SELL_LIMIT',
            'BUY_STOP', 'SELL_STOP', 'BUY_STOP_LIMIT', 'SELL_STOP_LIMIT'
        }
        actual_types = {order_type.name for order_type in OrderType}
        assert actual_types == expected_types

    def test_order_type_str(self):
        """Test string representation of OrderType."""
        assert str(OrderType.BUY) == "BUY"
        assert str(OrderType.SELL) == "SELL"
        assert str(OrderType.BUY_LIMIT) == "BUY_LIMIT"

    def test_order_type_repr(self):
        """Test detailed representation of OrderType."""
        assert repr(OrderType.BUY) == "OrderType.BUY"
        assert repr(OrderType.SELL_LIMIT) == "OrderType.SELL_LIMIT"

    def test_is_market_order(self):
        """Test is_market_order classification."""
        assert OrderType.is_market_order(OrderType.BUY) is True
        assert OrderType.is_market_order(OrderType.SELL) is True
        assert OrderType.is_market_order(OrderType.BUY_LIMIT) is False
        assert OrderType.is_market_order(OrderType.SELL_LIMIT) is False
        assert OrderType.is_market_order(OrderType.BUY_STOP) is False
        assert OrderType.is_market_order(OrderType.SELL_STOP) is False

    def test_is_pending_order(self):
        """Test is_pending_order classification."""
        assert OrderType.is_pending_order(OrderType.BUY) is False
        assert OrderType.is_pending_order(OrderType.SELL) is False
        assert OrderType.is_pending_order(OrderType.BUY_LIMIT) is True
        assert OrderType.is_pending_order(OrderType.SELL_LIMIT) is True
        assert OrderType.is_pending_order(OrderType.BUY_STOP) is True
        assert OrderType.is_pending_order(OrderType.SELL_STOP) is True
        assert OrderType.is_pending_order(OrderType.BUY_STOP_LIMIT) is True
        assert OrderType.is_pending_order(OrderType.SELL_STOP_LIMIT) is True

    def test_is_buy_order(self):
        """Test is_buy_order classification."""
        assert OrderType.is_buy_order(OrderType.BUY) is True
        assert OrderType.is_buy_order(OrderType.BUY_LIMIT) is True
        assert OrderType.is_buy_order(OrderType.BUY_STOP) is True
        assert OrderType.is_buy_order(OrderType.BUY_STOP_LIMIT) is True
        assert OrderType.is_buy_order(OrderType.SELL) is False
        assert OrderType.is_buy_order(OrderType.SELL_LIMIT) is False
        assert OrderType.is_buy_order(OrderType.SELL_STOP) is False
        assert OrderType.is_buy_order(OrderType.SELL_STOP_LIMIT) is False

    def test_is_sell_order(self):
        """Test is_sell_order classification."""
        assert OrderType.is_sell_order(OrderType.SELL) is True
        assert OrderType.is_sell_order(OrderType.SELL_LIMIT) is True
        assert OrderType.is_sell_order(OrderType.SELL_STOP) is True
        assert OrderType.is_sell_order(OrderType.SELL_STOP_LIMIT) is True
        assert OrderType.is_sell_order(OrderType.BUY) is False
        assert OrderType.is_sell_order(OrderType.BUY_LIMIT) is False
        assert OrderType.is_sell_order(OrderType.BUY_STOP) is False
        assert OrderType.is_sell_order(OrderType.BUY_STOP_LIMIT) is False


class TestTimeFrame:
    """Test suite for TimeFrame enum."""

    def test_timeframe_values(self):
        """Test that TimeFrame values match MT5 constants."""
        assert TimeFrame.M1 == mt5.TIMEFRAME_M1
        assert TimeFrame.M5 == mt5.TIMEFRAME_M5
        assert TimeFrame.M15 == mt5.TIMEFRAME_M15
        assert TimeFrame.M30 == mt5.TIMEFRAME_M30
        assert TimeFrame.H1 == mt5.TIMEFRAME_H1
        assert TimeFrame.H4 == mt5.TIMEFRAME_H4
        assert TimeFrame.D1 == mt5.TIMEFRAME_D1
        assert TimeFrame.W1 == mt5.TIMEFRAME_W1
        assert TimeFrame.MN1 == mt5.TIMEFRAME_MN1

    def test_timeframe_count(self):
        """Test that all expected timeframes are present."""
        expected_timeframes = {'M1', 'M5', 'M15', 'M30', 'H1', 'H4', 'D1', 'W1', 'MN1'}
        actual_timeframes = {tf.name for tf in TimeFrame}
        assert actual_timeframes == expected_timeframes

    def test_timeframe_str(self):
        """Test string representation of TimeFrame."""
        assert str(TimeFrame.M1) == "M1"
        assert str(TimeFrame.H1) == "H1"
        assert str(TimeFrame.D1) == "D1"

    def test_timeframe_repr(self):
        """Test detailed representation of TimeFrame."""
        assert repr(TimeFrame.M1) == "TimeFrame.M1"
        assert repr(TimeFrame.H4) == "TimeFrame.H4"

    def test_timeframe_minutes_property(self):
        """Test the minutes property for all timeframes."""
        assert TimeFrame.M1.minutes == 1
        assert TimeFrame.M5.minutes == 5
        assert TimeFrame.M15.minutes == 15
        assert TimeFrame.M30.minutes == 30
        assert TimeFrame.H1.minutes == 60
        assert TimeFrame.H4.minutes == 240
        assert TimeFrame.D1.minutes == 1440
        assert TimeFrame.W1.minutes == 10080
        assert TimeFrame.MN1.minutes == 43200

    def test_timeframe_from_string(self):
        """Test creating TimeFrame from string."""
        assert TimeFrame.from_string("M1") == TimeFrame.M1
        assert TimeFrame.from_string("m1") == TimeFrame.M1  # Case insensitive
        assert TimeFrame.from_string("H4") == TimeFrame.H4
        assert TimeFrame.from_string("D1") == TimeFrame.D1
        assert TimeFrame.from_string("W1") == TimeFrame.W1
        assert TimeFrame.from_string("MN1") == TimeFrame.MN1

    def test_timeframe_from_string_invalid(self):
        """Test that invalid strings raise ValueError."""
        with pytest.raises(ValueError, match="Invalid timeframe string"):
            TimeFrame.from_string("INVALID")

        with pytest.raises(ValueError, match="Invalid timeframe string"):
            TimeFrame.from_string("M2")

    def test_timeframe_from_minutes(self):
        """Test creating TimeFrame from minutes."""
        assert TimeFrame.from_minutes(1) == TimeFrame.M1
        assert TimeFrame.from_minutes(5) == TimeFrame.M5
        assert TimeFrame.from_minutes(15) == TimeFrame.M15
        assert TimeFrame.from_minutes(30) == TimeFrame.M30
        assert TimeFrame.from_minutes(60) == TimeFrame.H1
        assert TimeFrame.from_minutes(240) == TimeFrame.H4
        assert TimeFrame.from_minutes(1440) == TimeFrame.D1
        assert TimeFrame.from_minutes(10080) == TimeFrame.W1
        assert TimeFrame.from_minutes(43200) == TimeFrame.MN1

    def test_timeframe_from_minutes_invalid(self):
        """Test that invalid minutes raise ValueError."""
        with pytest.raises(ValueError, match="No timeframe matches"):
            TimeFrame.from_minutes(2)

        with pytest.raises(ValueError, match="No timeframe matches"):
            TimeFrame.from_minutes(100)


class TestEnumIntegration:
    """Integration tests for enum interactions."""

    def test_order_type_with_timeframe(self):
        """Test that different enums can be used together."""
        order = OrderType.BUY
        timeframe = TimeFrame.H1

        assert OrderType.is_buy_order(order)
        assert timeframe.minutes == 60
        # This tests that the enums are independent

    def test_connection_state_transitions(self):
        """Test typical connection state transitions."""
        states = [
            ConnectionState.DISCONNECTED,
            ConnectionState.INITIALIZING,
            ConnectionState.CONNECTED
        ]

        assert len(states) == 3
        assert states[0] == ConnectionState.DISCONNECTED
        assert states[-1] == ConnectionState.CONNECTED

    def test_enum_uniqueness(self):
        """Test that enum values are unique within each enum."""
        # ConnectionState values should be unique
        conn_values = [state.value for state in ConnectionState]
        assert len(conn_values) == len(set(conn_values))

        # OrderType values should be unique
        order_values = [order.value for order in OrderType]
        assert len(order_values) == len(set(order_values))

        # TimeFrame values should be unique
        tf_values = [tf.value for tf in TimeFrame]
        assert len(tf_values) == len(set(tf_values))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
