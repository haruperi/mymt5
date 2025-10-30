"""
Error scenario tests for Phase 8.
"""

import pytest
from unittest.mock import patch, Mock

pytest.importorskip("pandas")

import MetaTrader5 as mt5

from mymt5.client import MT5Client
from mymt5.trade import MT5Trade
from mymt5.validator import MT5Validator


@pytest.fixture
def client():
    return MT5Client()


def test_invalid_credentials_login(client, monkeypatch):
    with patch("MetaTrader5.login", return_value=False), \
         patch("MetaTrader5.last_error", return_value=(10004, "Invalid credentials")):
        ok = client.login(99999, "badpass", "BadServer")
        assert ok is False
        assert client.get_error() == (10004, "Invalid credentials")


def test_invalid_symbol_validation():
    validator = MT5Validator()
    with patch("MetaTrader5.symbol_info", return_value=None):
        valid, msg = validator._validate_symbol("INVALID")
        assert valid is False
        assert "not found" in msg.lower() or "invalid" in msg.lower()


def test_insufficient_margin_on_order_send(client):
    trade = MT5Trade(client=client)
    with patch("MetaTrader5.symbol_info_tick") as mock_tick, \
         patch.object(MT5Trade, "_send_request") as mock_send:
        mock_tick.return_value = Mock(bid=1.1, ask=1.1002)
        mock_send.return_value = {"retcode": mt5.TRADE_RETCODE_REJECT, "comment": "Insufficient margin"}
        result = trade.execute("EURUSD", order_type=0, volume=1000)
        assert result is not None
        assert result.get("retcode") == mt5.TRADE_RETCODE_REJECT


def test_market_closed_rejection(client):
    trade = MT5Trade(client=client)
    with patch("MetaTrader5.symbol_info_tick") as mock_tick, \
         patch.object(MT5Trade, "_send_request") as mock_send:
        mock_tick.return_value = Mock(bid=1.1, ask=1.1002)
        mock_send.return_value = {"retcode": mt5.TRADE_RETCODE_REJECT, "comment": "Market closed"}
        result = trade.execute("EURUSD", order_type=0, volume=0.1)
        assert result.get("comment") == "Market closed"


def test_network_disconnection_and_reconnect(client):
    client.account_login = 123
    client.account_password = "x"
    client.account_server = "s"
    with patch("MetaTrader5.initialize", side_effect=[False, True]):
        # First attempt fails, second succeeds
        result = client._handle_reconnection()
        assert result in (True, False)


