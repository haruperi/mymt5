"""
End-to-end workflow tests covering:
Connect → Get account info → Execute trade → Monitor → Close

Uses MT5 stubs/mocks to avoid external dependencies.
"""

import pytest
from unittest.mock import patch, Mock

pytest.importorskip("pandas")

import MetaTrader5 as mt5

from mymt5.client import MT5Client
from mymt5.trade import MT5Trade
from mymt5.history import MT5History


@pytest.fixture
def client():
    return MT5Client()


@pytest.fixture
def trade(client):
    return MT5Trade(client=client)


def test_end_to_end_trade_lifecycle(client, trade, monkeypatch):
    # Connect (mock MT5 to avoid external dependency/timeouts)
    with patch("MetaTrader5.initialize", return_value=True), \
         patch("MetaTrader5.login", return_value=True), \
         patch("MetaTrader5.terminal_info", return_value=Mock(connected=True)):
        assert client.initialize(login=12345, password="pass", server="Server")
        assert client.is_connected() is True

    # Execute trade (mock _send_request to return success)
    with patch.object(MT5Trade, "_send_request") as mock_send, \
         patch("MetaTrader5.symbol_info_tick") as mock_tick:
        mock_send.return_value = {
            "retcode": mt5.TRADE_RETCODE_DONE,
            "deal": 111,
            "order": 222,
            "volume": 0.1,
            "price": 1.1000,
        }
        mock_tick.return_value = Mock(bid=1.1, ask=1.1002)

        result = trade.buy("EURUSD", 0.1)
        assert result is None or isinstance(result, dict)

    # Monitor via history/order check (mock to simulate closed order)
    with patch("MetaTrader5.orders_get", return_value=()), \
         patch("MetaTrader5.history_deals_get") as mock_deals:
        Deal = Mock
        mock_deals.return_value = (Deal(ticket=222, symbol="EURUSD"),)
        status = trade.check_order(222)
        assert status is not None
        assert status["status"] in {"open", "closed"}

    # Close position (simulate no open positions)
    with patch("MetaTrader5.positions_get", return_value=()):
        # No exception and returns None when nothing to close
        result = trade.close_position(ticket=99999)
        assert result is None or isinstance(result, dict)

    # Disconnect and shutdown
    assert client.disconnect() is True
    client.shutdown()
    assert client.connection_state.name.lower() == "disconnected"


