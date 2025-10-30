from mylogger import logger
"""
Unit tests for MT5Trade class.
"""

import pytest
import pandas as pd
from unittest.mock import Mock, MagicMock, patch
import MetaTrader5 as mt5
from collections import namedtuple
from datetime import datetime

from mymt5.trade import MT5Trade
from mymt5.enums import OrderType


@pytest.fixture
def mock_client():
    """Create a mock MT5Client."""
    client = Mock()
    client.is_connected.return_value = True
    return client


@pytest.fixture
def mt5_trade(mock_client):
    """Create MT5Trade instance with mock client."""
    return MT5Trade(client=mock_client)


@pytest.fixture
def mock_symbol_info():
    """Create mock symbol info."""
    info = Mock()
    info.volume_min = 0.01
    info.volume_max = 100.0
    info.volume_step = 0.01
    return info


@pytest.fixture
def mock_tick():
    """Create mock tick."""
    tick = Mock()
    tick.bid = 1.1300
    tick.ask = 1.1302
    tick.last = 1.1301
    return tick


@pytest.fixture
def mock_order_result():
    """Create mock order result."""
    result = Mock()
    result.retcode = mt5.TRADE_RETCODE_DONE
    result.deal = 12345
    result.order = 67890
    result.volume = 0.1
    result.price = 1.1300
    result.bid = 1.1300
    result.ask = 1.1302
    result.comment = "Request executed"
    result.request_id = 1
    result.retcode_external = 0
    return result


class TestMT5TradeInitialization:
    """Test MT5Trade initialization."""

    def test_init_with_client(self, mock_client):
        """Test initialization with client."""
        trade = MT5Trade(client=mock_client)
        assert trade.client == mock_client

    def test_init_without_client(self):
        """Test initialization without client."""
        trade = MT5Trade()
        assert trade.client is None


class TestBuildRequest:
    """Test request building."""

    @patch('MetaTrader5.symbol_info_tick')
    def test_build_market_buy_request(self, mock_tick_func, mt5_trade, mock_tick):
        """Test building market buy request."""
        mock_tick_func.return_value = mock_tick

        request = mt5_trade.build_request(
            symbol="EURUSD",
            order_type=OrderType.BUY,
            volume=0.1,
            sl=1.1250,
            tp=1.1350
        )

        assert request is not None
        assert request['symbol'] == 'EURUSD'
        assert request['volume'] == 0.1
        assert request['type'] == mt5.ORDER_TYPE_BUY
        assert request['sl'] == 1.1250
        assert request['tp'] == 1.1350
        assert request['action'] == mt5.TRADE_ACTION_DEAL

    @patch('MetaTrader5.symbol_info_tick')
    def test_build_pending_order_request(self, mock_tick_func, mt5_trade, mock_tick):
        """Test building pending order request."""
        mock_tick_func.return_value = mock_tick

        request = mt5_trade.build_request(
            symbol="EURUSD",
            order_type=OrderType.BUY_LIMIT,
            volume=0.1,
            price=1.1280
        )

        assert request is not None
        assert request['action'] == mt5.TRADE_ACTION_PENDING
        assert request['price'] == 1.1280

    @patch('MetaTrader5.symbol_info_tick')
    def test_build_request_no_tick(self, mock_tick_func, mt5_trade):
        """Test building request when tick fails."""
        mock_tick_func.return_value = None

        request = mt5_trade.build_request(
            symbol="INVALID",
            order_type=OrderType.BUY,
            volume=0.1
        )

        assert request is None


class TestOrderExecution:
    """Test order execution methods."""

    @patch.object(MT5Trade, '_send_request')
    @patch.object(MT5Trade, 'build_request')
    def test_execute_success(self, mock_build, mock_send, mt5_trade, mock_order_result):
        """Test successful order execution."""
        mock_build.return_value = {'action': mt5.TRADE_ACTION_DEAL}
        mock_send.return_value = mock_order_result.__dict__

        result = mt5_trade.execute("EURUSD", OrderType.BUY, 0.1)

        assert result is not None
        mock_build.assert_called_once()
        mock_send.assert_called_once()

    @patch.object(MT5Trade, 'execute')
    def test_buy_simplified(self, mock_execute, mt5_trade):
        """Test simplified buy method."""
        mt5_trade.buy("EURUSD", 0.1, sl=1.1250, tp=1.1350)

        mock_execute.assert_called_once()
        args = mock_execute.call_args[0]
        assert args[0] == "EURUSD"
        assert args[1] == OrderType.BUY
        assert args[2] == 0.1

    @patch.object(MT5Trade, 'execute')
    def test_sell_simplified(self, mock_execute, mt5_trade):
        """Test simplified sell method."""
        mt5_trade.sell("EURUSD", 0.1, sl=1.1350, tp=1.1250)

        mock_execute.assert_called_once()
        args = mock_execute.call_args[0]
        assert args[1] == OrderType.SELL

    @patch('MetaTrader5.order_send')
    def test_send_request_success(self, mock_order_send, mt5_trade, mock_order_result):
        """Test sending request successfully."""
        mock_order_send.return_value = mock_order_result

        result = mt5_trade._send_request({'action': mt5.TRADE_ACTION_DEAL})

        assert result is not None
        assert result['retcode'] == mt5.TRADE_RETCODE_DONE
        assert result['deal'] == 12345

    @patch('MetaTrader5.order_send')
    def test_send_request_failure(self, mock_order_send, mt5_trade):
        """Test sending request failure."""
        mock_result = Mock()
        mock_result.retcode = mt5.TRADE_RETCODE_REJECT
        mock_result.comment = "Request rejected"
        mock_order_send.return_value = mock_result

        result = mt5_trade._send_request({'action': mt5.TRADE_ACTION_DEAL})

        assert result is not None
        assert result['retcode'] == mt5.TRADE_RETCODE_REJECT


class TestOrderManagement:
    """Test order management methods."""

    @patch('MetaTrader5.orders_get')
    def test_get_orders_all(self, mock_orders_get, mt5_trade):
        """Test getting all orders."""
        Order = namedtuple('Order', ['ticket', 'symbol', 'type', 'volume', 'time_setup'])
        mock_orders_get.return_value = (
            Order(1, 'EURUSD', mt5.ORDER_TYPE_BUY_LIMIT, 0.1, 1640000000),
            Order(2, 'GBPUSD', mt5.ORDER_TYPE_SELL_LIMIT, 0.2, 1640003600),
        )

        result = mt5_trade.get_orders()

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2

    @patch('MetaTrader5.orders_get')
    def test_get_orders_by_symbol(self, mock_orders_get, mt5_trade):
        """Test getting orders by symbol."""
        mock_orders_get.return_value = ()

        result = mt5_trade.get_orders(symbol="EURUSD")

        assert isinstance(result, pd.DataFrame)
        mock_orders_get.assert_called_with(symbol="EURUSD")

    @patch('MetaTrader5.orders_get')
    def test_get_orders_empty(self, mock_orders_get, mt5_trade):
        """Test getting orders when none exist."""
        mock_orders_get.return_value = ()

        result = mt5_trade.get_orders()

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0

    @patch.object(MT5Trade, '_send_request')
    @patch('MetaTrader5.orders_get')
    def test_modify_order(self, mock_orders_get, mock_send, mt5_trade):
        """Test modifying an order."""
        Order = namedtuple('Order', ['ticket', 'symbol', 'type', 'volume_current',
                                     'price_open', 'sl', 'tp'])
        mock_orders_get.return_value = (
            Order(12345, 'EURUSD', mt5.ORDER_TYPE_BUY_LIMIT, 0.1, 1.1280, 1.1250, 1.1350),
        )
        mock_send.return_value = {'retcode': mt5.TRADE_RETCODE_DONE}

        result = mt5_trade.modify_order(12345, price=1.1290)

        assert result is not None
        mock_send.assert_called_once()

    @patch('MetaTrader5.orders_get')
    def test_modify_order_not_found(self, mock_orders_get, mt5_trade):
        """Test modifying non-existent order."""
        mock_orders_get.return_value = ()

        result = mt5_trade.modify_order(99999)

        assert result is None

    @patch.object(MT5Trade, '_send_request')
    def test_cancel_order_single(self, mock_send, mt5_trade):
        """Test cancelling a single order."""
        mock_send.return_value = {'retcode': mt5.TRADE_RETCODE_DONE}

        result = mt5_trade.cancel_order(ticket=12345)

        assert result is not None
        mock_send.assert_called_once()

    @patch.object(MT5Trade, '_send_request')
    @patch.object(MT5Trade, 'get_orders')
    def test_cancel_orders_all(self, mock_get, mock_send, mt5_trade):
        """Test cancelling all orders."""
        mock_get.return_value = pd.DataFrame([
            {'ticket': 1, 'symbol': 'EURUSD'},
            {'ticket': 2, 'symbol': 'GBPUSD'},
        ])
        mock_send.return_value = {'retcode': mt5.TRADE_RETCODE_DONE}

        result = mt5_trade.cancel_order(cancel_all=True)

        assert isinstance(result, list)
        assert len(result) == 2


class TestPositionManagement:
    """Test position management methods."""

    @patch('MetaTrader5.positions_get')
    def test_get_positions_all(self, mock_positions_get, mt5_trade):
        """Test getting all positions."""
        Position = namedtuple('Position', ['ticket', 'symbol', 'type', 'volume',
                                           'price_open', 'profit', 'time'])
        mock_positions_get.return_value = (
            Position(1, 'EURUSD', mt5.POSITION_TYPE_BUY, 0.1, 1.1300, 50.0, 1640000000),
            Position(2, 'GBPUSD', mt5.POSITION_TYPE_SELL, 0.2, 1.1800, -30.0, 1640003600),
        )

        result = mt5_trade.get_positions()

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2

    @patch('MetaTrader5.positions_get')
    def test_get_positions_empty(self, mock_positions_get, mt5_trade):
        """Test getting positions when none exist."""
        mock_positions_get.return_value = ()

        result = mt5_trade.get_positions()

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0

    @patch.object(MT5Trade, '_send_request')
    @patch('MetaTrader5.positions_get')
    def test_modify_position(self, mock_positions_get, mock_send, mt5_trade):
        """Test modifying a position."""
        Position = namedtuple('Position', ['ticket', 'symbol', 'sl', 'tp'])
        mock_positions_get.return_value = (
            Position(12345, 'EURUSD', 1.1250, 1.1350),
        )
        mock_send.return_value = {'retcode': mt5.TRADE_RETCODE_DONE}

        result = mt5_trade.modify_position("EURUSD", sl=1.1260)

        assert result is not None
        mock_send.assert_called_once()

    @patch.object(MT5Trade, '_send_request')
    @patch('MetaTrader5.symbol_info_tick')
    @patch('MetaTrader5.positions_get')
    def test_close_position(self, mock_positions_get, mock_tick, mock_send, mt5_trade):
        """Test closing a position."""
        Position = namedtuple('Position', ['ticket', 'symbol', 'type', 'volume', 'magic'])
        mock_positions_get.return_value = (
            Position(12345, 'EURUSD', mt5.POSITION_TYPE_BUY, 0.1, 0),
        )
        mock_tick.return_value = Mock(bid=1.1300, ask=1.1302)
        mock_send.return_value = {'retcode': mt5.TRADE_RETCODE_DONE}

        result = mt5_trade.close_position(ticket=12345)

        assert result is not None
        mock_send.assert_called_once()

    @patch.object(MT5Trade, '_send_request')
    @patch('MetaTrader5.symbol_info_tick')
    @patch('MetaTrader5.positions_get')
    def test_close_position_partial(self, mock_positions_get, mock_tick, mock_send, mt5_trade):
        """Test partial position close."""
        Position = namedtuple('Position', ['ticket', 'symbol', 'type', 'volume', 'magic'])
        mock_positions_get.return_value = (
            Position(12345, 'EURUSD', mt5.POSITION_TYPE_BUY, 0.1, 0),
        )
        mock_tick.return_value = Mock(bid=1.1300, ask=1.1302)
        mock_send.return_value = {'retcode': mt5.TRADE_RETCODE_DONE}

        result = mt5_trade.close_position(ticket=12345, volume=0.05)

        assert result is not None
        # Check that volume in request was 0.05
        call_args = mock_send.call_args[0][0]
        assert call_args['volume'] == 0.05

    @patch.object(MT5Trade, 'sell')
    @patch('MetaTrader5.positions_get')
    def test_reverse_position_buy(self, mock_positions_get, mock_sell, mt5_trade):
        """Test reversing a buy position."""
        Position = namedtuple('Position', ['ticket', 'symbol', 'type', 'volume'])
        mock_positions_get.return_value = (
            Position(12345, 'EURUSD', mt5.POSITION_TYPE_BUY, 0.1),
        )

        mt5_trade.reverse_position("EURUSD")

        # Should sell double the volume
        mock_sell.assert_called_once_with("EURUSD", 0.2)


class TestPositionAnalytics:
    """Test position analytics methods."""

    @patch('MetaTrader5.symbol_info_tick')
    @patch('MetaTrader5.positions_get')
    def test_analyze_position_profit(self, mock_positions_get, mock_tick, mt5_trade):
        """Test analyzing position profit."""
        Position = namedtuple('Position', ['ticket', 'symbol', 'profit'])
        mock_positions_get.return_value = (
            Position(12345, 'EURUSD', 50.0),
        )

        result = mt5_trade.analyze_position(ticket=12345, metric='profit')

        assert result == 50.0

    @patch('MetaTrader5.symbol_info_tick')
    @patch('MetaTrader5.positions_get')
    def test_analyze_position_all(self, mock_positions_get, mock_tick, mt5_trade):
        """Test analyzing all position metrics."""
        Position = namedtuple('Position', ['ticket', 'symbol', 'type', 'volume',
                                           'price_open', 'profit', 'sl', 'tp', 'time'])
        mock_positions_get.return_value = (
            Position(12345, 'EURUSD', mt5.POSITION_TYPE_BUY, 0.1, 1.1300, 50.0,
                    1.1250, 1.1350, 1640000000),
        )
        mock_tick.return_value = Mock(bid=1.1350, ask=1.1352)

        result = mt5_trade.analyze_position(ticket=12345, metric='all')

        assert isinstance(result, dict)
        assert result['ticket'] == 12345
        assert result['profit'] == 50.0
        assert 'duration' in result

    @patch('MetaTrader5.positions_get')
    def test_get_position_stats(self, mock_positions_get, mt5_trade):
        """Test getting position statistics."""
        Position = namedtuple('Position', ['ticket', 'symbol', 'type', 'volume',
                                           'profit', 'time'])
        mock_positions_get.return_value = (
            Position(1, 'EURUSD', mt5.POSITION_TYPE_BUY, 0.1, 50.0, 1640000000),
            Position(2, 'GBPUSD', mt5.POSITION_TYPE_SELL, 0.2, -30.0, 1640003600),
            Position(3, 'EURUSD', mt5.POSITION_TYPE_BUY, 0.1, 20.0, 1640007200),
        )

        result = mt5_trade.get_position_stats()

        assert result['total_positions'] == 3
        assert result['total_volume'] == 0.4
        assert result['total_profit'] == 40.0
        assert result['buy_positions'] == 2
        assert result['sell_positions'] == 1
        assert result['profitable_positions'] == 2
        assert result['losing_positions'] == 1

    @patch('MetaTrader5.positions_get')
    def test_get_position_stats_empty(self, mock_positions_get, mt5_trade):
        """Test getting stats with no positions."""
        mock_positions_get.return_value = ()

        result = mt5_trade.get_position_stats()

        assert result['total_positions'] == 0
        assert result['total_profit'] == 0.0


class TestValidation:
    """Test validation methods."""

    @patch('MetaTrader5.symbol_info')
    def test_validate_request_success(self, mock_symbol_info, mt5_trade):
        """Test successful request validation."""
        mock_info = Mock()
        mock_info.volume_min = 0.01
        mock_info.volume_max = 100.0
        mock_symbol_info.return_value = mock_info

        request = {
            'action': mt5.TRADE_ACTION_DEAL,
            'symbol': 'EURUSD',
            'volume': 0.1,
            'type': mt5.ORDER_TYPE_BUY
        }

        valid, msg = mt5_trade.validate_request(request)

        assert valid is True
        assert msg == "Request is valid"

    @patch('MetaTrader5.symbol_info')
    def test_validate_request_missing_field(self, mock_symbol_info, mt5_trade):
        """Test validation with missing field."""
        request = {
            'action': mt5.TRADE_ACTION_DEAL,
            'symbol': 'EURUSD',
        }

        valid, msg = mt5_trade.validate_request(request)

        assert valid is False
        assert 'Missing required field' in msg

    @patch('MetaTrader5.symbol_info')
    def test_validate_request_invalid_volume(self, mock_symbol_info, mt5_trade):
        """Test validation with invalid volume."""
        mock_info = Mock()
        mock_info.volume_min = 0.01
        mock_info.volume_max = 100.0
        mock_symbol_info.return_value = mock_info

        request = {
            'action': mt5.TRADE_ACTION_DEAL,
            'symbol': 'EURUSD',
            'volume': 0.001,  # Below minimum
            'type': mt5.ORDER_TYPE_BUY
        }

        valid, msg = mt5_trade.validate_request(request)

        assert valid is False
        assert 'below minimum' in msg

    @patch('MetaTrader5.orders_get')
    @patch('MetaTrader5.history_deals_get')
    def test_check_order_open(self, mock_deals, mock_orders, mt5_trade):
        """Test checking open order."""
        Order = namedtuple('Order', ['ticket', 'symbol'])
        mock_orders.return_value = (Order(12345, 'EURUSD'),)

        result = mt5_trade.check_order(12345)

        assert result is not None
        assert result['status'] == 'open'
        assert result['ticket'] == 12345

    @patch('MetaTrader5.orders_get')
    @patch('MetaTrader5.history_deals_get')
    def test_check_order_closed(self, mock_deals, mock_orders, mt5_trade):
        """Test checking closed order."""
        mock_orders.return_value = ()
        Deal = namedtuple('Deal', ['ticket', 'symbol'])
        mock_deals.return_value = (Deal(12345, 'EURUSD'),)

        result = mt5_trade.check_order(12345)

        assert result is not None
        assert result['status'] == 'closed'


class TestUtilityMethods:
    """Test utility methods."""

    @patch.object(MT5Trade, 'get_positions')
    @patch.object(MT5Trade, 'get_orders')
    @patch.object(MT5Trade, 'get_position_stats')
    def test_get_summary(self, mock_stats, mock_orders, mock_positions, mt5_trade):
        """Test getting trading summary."""
        mock_positions.return_value = pd.DataFrame([{'ticket': 1}])
        mock_orders.return_value = pd.DataFrame([{'ticket': 1, 'symbol': 'EURUSD'}])
        mock_stats.return_value = {'total_positions': 1}

        result = mt5_trade.get_summary()

        assert isinstance(result, dict)
        assert 'positions' in result
        assert 'orders' in result

    @patch.object(MT5Trade, 'get_summary')
    def test_export_json(self, mock_summary, mt5_trade, tmp_path):
        """Test exporting summary to JSON."""
        mock_summary.return_value = {'positions': {'total': 1}, 'orders': {'total': 0}}

        filepath = tmp_path / "summary.json"
        result = mt5_trade.export(filepath, format='json')

        assert result is True
        assert filepath.exists()

    @patch.object(MT5Trade, 'get_summary')
    def test_export_csv(self, mock_summary, mt5_trade, tmp_path):
        """Test exporting summary to CSV."""
        mock_summary.return_value = {'positions': {'total': 1}}

        filepath = tmp_path / "summary.csv"
        result = mt5_trade.export(filepath, format='csv')

        assert result is True
        assert filepath.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
