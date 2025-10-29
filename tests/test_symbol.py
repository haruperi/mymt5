"""Tests for MT5Symbol class"""

from mylogger import logger
import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
from mymt5.symbol import MT5Symbol


@pytest.fixture
def mock_client():
    """Create a mock MT5Client instance"""
    client = Mock()
    client.is_connected.return_value = True
    return client


@pytest.fixture
def mock_symbol_info():
    """Create mock symbol info"""
    symbol_info = Mock()
    symbol_info.name = "EURUSD"
    symbol_info.custom = False
    symbol_info.chart_mode = 0
    symbol_info.select = True
    symbol_info.visible = True
    symbol_info.session_deals = 1000
    symbol_info.session_buy_orders = 500
    symbol_info.session_sell_orders = 500
    symbol_info.volume = 100
    symbol_info.volumehigh = 150
    symbol_info.volumelow = 50
    symbol_info.time = int(datetime.now().timestamp())
    symbol_info.digits = 5
    symbol_info.spread = 10
    symbol_info.spread_float = True
    symbol_info.ticks_bookdepth = 10
    symbol_info.trade_calc_mode = 0
    symbol_info.trade_mode = 4  # Full access
    symbol_info.start_time = 0
    symbol_info.expiration_time = 0
    symbol_info.trade_stops_level = 0
    symbol_info.trade_freeze_level = 0
    symbol_info.trade_exemode = 0
    symbol_info.swap_mode = 0
    symbol_info.swap_rollover3days = 3
    symbol_info.margin_hedged_use_leg = False
    symbol_info.expiration_mode = 15
    symbol_info.filling_mode = 1
    symbol_info.order_mode = 127
    symbol_info.order_gtc_mode = 0
    symbol_info.option_mode = 0
    symbol_info.option_right = 0
    symbol_info.bid = 1.09234
    symbol_info.bidhigh = 1.09500
    symbol_info.bidlow = 1.09000
    symbol_info.ask = 1.09245
    symbol_info.askhigh = 1.09510
    symbol_info.asklow = 1.09010
    symbol_info.last = 1.09240
    symbol_info.lasthigh = 1.09505
    symbol_info.lastlow = 1.09005
    symbol_info.volume_real = 100.0
    symbol_info.volumehigh_real = 150.0
    symbol_info.volumelow_real = 50.0
    symbol_info.option_strike = 0.0
    symbol_info.point = 0.00001
    symbol_info.trade_tick_value = 1.0
    symbol_info.trade_tick_value_profit = 1.0
    symbol_info.trade_tick_value_loss = 1.0
    symbol_info.trade_tick_size = 0.00001
    symbol_info.trade_contract_size = 100000.0
    symbol_info.trade_accrued_interest = 0.0
    symbol_info.trade_face_value = 0.0
    symbol_info.trade_liquidity_rate = 0.0
    symbol_info.volume_min = 0.01
    symbol_info.volume_max = 100.0
    symbol_info.volume_step = 0.01
    symbol_info.volume_limit = 0.0
    symbol_info.swap_long = -0.5
    symbol_info.swap_short = 0.3
    symbol_info.margin_initial = 0.0
    symbol_info.margin_maintenance = 0.0
    symbol_info.session_volume = 1000.0
    symbol_info.session_turnover = 100000.0
    symbol_info.session_interest = 0.0
    symbol_info.session_buy_orders_volume = 500.0
    symbol_info.session_sell_orders_volume = 500.0
    symbol_info.session_open = 1.09200
    symbol_info.session_close = 1.09300
    symbol_info.session_aw = 1.09250
    symbol_info.session_price_settlement = 0.0
    symbol_info.session_price_limit_min = 0.0
    symbol_info.session_price_limit_max = 0.0
    symbol_info.margin_hedged = 0.0
    symbol_info.price_change = 0.05
    symbol_info.price_volatility = 0.0
    symbol_info.price_theoretical = 0.0
    symbol_info.price_greeks_delta = 0.0
    symbol_info.price_greeks_theta = 0.0
    symbol_info.price_greeks_gamma = 0.0
    symbol_info.price_greeks_vega = 0.0
    symbol_info.price_greeks_rho = 0.0
    symbol_info.price_greeks_omega = 0.0
    symbol_info.price_sensitivity = 0.0
    symbol_info.basis = ""
    symbol_info.category = ""
    symbol_info.currency_base = "EUR"
    symbol_info.currency_profit = "USD"
    symbol_info.currency_margin = "USD"
    symbol_info.bank = ""
    symbol_info.description = "Euro vs US Dollar"
    symbol_info.exchange = ""
    symbol_info.formula = ""
    symbol_info.isin = ""
    symbol_info.page = ""
    symbol_info.path = "Forex\\EURUSD"
    return symbol_info


@pytest.fixture
def symbol(mock_client):
    """Create MT5Symbol instance"""
    return MT5Symbol(mock_client)


class TestMT5SymbolInit:
    """Test MT5Symbol initialization"""

    def test_init(self, mock_client):
        """Test symbol initialization"""
        symbol = MT5Symbol(mock_client)
        assert symbol.client == mock_client
        assert symbol._symbol_info_cache == {}
        assert symbol._cache_timestamp == {}
        assert symbol._cache_duration == 1
        assert symbol._subscriptions == set()


class TestSymbolDiscovery:
    """Test symbol discovery methods"""

    @patch('mymt5.symbol.mt5')
    def test_get_symbols_all(self, mock_mt5, symbol, mock_symbol_info):
        """Test getting all symbols"""
        mock_symbols = [mock_symbol_info, mock_symbol_info]
        mock_mt5.symbols_get.return_value = mock_symbols

        result = symbol.get_symbols('all')

        assert isinstance(result, list)
        assert len(result) == 2
        assert all(s == "EURUSD" for s in result)

    @patch('mymt5.symbol.mt5')
    def test_get_symbols_market_watch(self, mock_mt5, symbol, mock_symbol_info):
        """Test getting market watch symbols"""
        mock_symbol_info.visible = True
        mock_symbols = [mock_symbol_info]
        mock_mt5.symbols_get.return_value = mock_symbols

        result = symbol.get_symbols('market_watch')

        assert isinstance(result, list)
        assert len(result) == 1

    @patch('mymt5.symbol.mt5')
    def test_get_symbols_group(self, mock_mt5, symbol, mock_symbol_info):
        """Test getting symbols by group"""
        mock_symbols = [mock_symbol_info]
        mock_mt5.symbols_get.return_value = mock_symbols

        result = symbol.get_symbols('group', 'Forex*')

        assert isinstance(result, list)
        mock_mt5.symbols_get.assert_called_with(group='Forex*')

    def test_get_symbols_invalid_filter(self, symbol):
        """Test invalid filter type raises ValueError"""
        with pytest.raises(ValueError):
            symbol.get_symbols('invalid_filter')

    def test_get_symbols_group_without_pattern(self, symbol):
        """Test group filter without pattern raises ValueError"""
        with pytest.raises(ValueError):
            symbol.get_symbols('group')


class TestMarketWatchManagement:
    """Test market watch management methods"""

    @patch('mymt5.symbol.mt5')
    def test_initialize_symbol(self, mock_mt5, symbol):
        """Test initializing symbol"""
        mock_mt5.symbol_select.return_value = True

        result = symbol.initialize('EURUSD')

        assert result is True
        mock_mt5.symbol_select.assert_called_with('EURUSD', True)

    @patch('mymt5.symbol.mt5')
    def test_manage_add(self, mock_mt5, symbol):
        """Test adding symbol to market watch"""
        mock_mt5.symbol_select.return_value = True

        result = symbol.manage('add', 'EURUSD')

        assert result is True
        mock_mt5.symbol_select.assert_called_with('EURUSD', True)

    @patch('mymt5.symbol.mt5')
    def test_manage_remove(self, mock_mt5, symbol):
        """Test removing symbol from market watch"""
        mock_mt5.symbol_select.return_value = True

        result = symbol.manage('remove', 'EURUSD')

        assert result is True
        mock_mt5.symbol_select.assert_called_with('EURUSD', False)

    def test_manage_invalid_action(self, symbol):
        """Test invalid action raises ValueError"""
        with pytest.raises(ValueError):
            symbol.manage('invalid_action', 'EURUSD')


class TestSymbolInformation:
    """Test symbol information methods"""

    @patch('mymt5.symbol.mt5')
    def test_get_info_all(self, mock_mt5, symbol, mock_symbol_info):
        """Test getting all symbol information"""
        mock_mt5.symbol_info.return_value = mock_symbol_info

        result = symbol.get_info('EURUSD')

        assert isinstance(result, dict)
        assert result['name'] == 'EURUSD'
        assert result['bid'] == 1.09234
        assert result['ask'] == 1.09245

    @patch('mymt5.symbol.mt5')
    def test_get_info_specific_attribute(self, mock_mt5, symbol, mock_symbol_info):
        """Test getting specific symbol attribute"""
        mock_mt5.symbol_info.return_value = mock_symbol_info

        bid = symbol.get_info('EURUSD', 'bid')
        assert bid == 1.09234

        ask = symbol.get_info('EURUSD', 'ask')
        assert ask == 1.09245

    @patch('mymt5.symbol.mt5')
    def test_get_info_invalid_attribute(self, mock_mt5, symbol, mock_symbol_info):
        """Test getting invalid attribute raises ValueError"""
        mock_mt5.symbol_info.return_value = mock_symbol_info

        with pytest.raises(ValueError):
            symbol.get_info('EURUSD', 'invalid_attribute')

    @patch('mymt5.symbol.mt5')
    def test_get_info_failed(self, mock_mt5, symbol):
        """Test failed symbol info retrieval"""
        mock_mt5.symbol_info.return_value = None
        mock_mt5.last_error.return_value = (1, "Symbol not found")

        with pytest.raises(RuntimeError):
            symbol.get_info('INVALID')

    @patch('mymt5.symbol.mt5')
    def test_info_caching(self, mock_mt5, symbol, mock_symbol_info):
        """Test symbol info caching"""
        mock_mt5.symbol_info.return_value = mock_symbol_info

        # First call
        result1 = symbol.get_info('EURUSD')
        # Second call should use cache
        result2 = symbol.get_info('EURUSD')

        assert result1 == result2
        # Should only call MT5 API once due to caching
        assert mock_mt5.symbol_info.call_count == 1


class TestSymbolStatus:
    """Test symbol status check methods"""

    @patch('mymt5.symbol.mt5')
    def test_check_available(self, mock_mt5, symbol, mock_symbol_info):
        """Test checking if symbol is available"""
        mock_mt5.symbol_info.return_value = mock_symbol_info

        result = symbol.check('EURUSD', 'available')

        assert result is True

    @patch('mymt5.symbol.mt5')
    def test_check_visible(self, mock_mt5, symbol, mock_symbol_info):
        """Test checking if symbol is visible"""
        mock_mt5.symbol_info.return_value = mock_symbol_info
        mock_symbol_info.visible = True

        result = symbol.check('EURUSD', 'visible')

        assert result is True

    @patch('mymt5.symbol.mt5')
    def test_check_tradable(self, mock_mt5, symbol, mock_symbol_info):
        """Test checking if symbol is tradable"""
        mock_mt5.symbol_info.return_value = mock_symbol_info
        mock_symbol_info.trade_mode = 4  # Full access

        result = symbol.check('EURUSD', 'tradable')

        assert result is True

    def test_check_invalid_status(self, symbol):
        """Test invalid status type raises ValueError"""
        with pytest.raises(ValueError):
            symbol.check('EURUSD', 'invalid_status')


class TestRealTimePrices:
    """Test real-time price methods"""

    @patch('mymt5.symbol.mt5')
    def test_get_price_bid(self, mock_mt5, symbol, mock_symbol_info):
        """Test getting bid price"""
        mock_mt5.symbol_info.return_value = mock_symbol_info

        price = symbol.get_price('EURUSD', 'bid')

        assert price == 1.09234

    @patch('mymt5.symbol.mt5')
    def test_get_price_ask(self, mock_mt5, symbol, mock_symbol_info):
        """Test getting ask price"""
        mock_mt5.symbol_info.return_value = mock_symbol_info

        price = symbol.get_price('EURUSD', 'ask')

        assert price == 1.09245

    @patch('mymt5.symbol.mt5')
    def test_get_price_current(self, mock_mt5, symbol, mock_symbol_info):
        """Test getting current prices"""
        mock_mt5.symbol_info.return_value = mock_symbol_info

        price = symbol.get_price('EURUSD', 'current')

        assert isinstance(price, dict)
        assert price['bid'] == 1.09234
        assert price['ask'] == 1.09245
        assert 'spread' in price

    def test_get_price_invalid_type(self, symbol):
        """Test invalid price type raises ValueError"""
        with pytest.raises(ValueError):
            symbol.get_price('EURUSD', 'invalid_type')


class TestMarketDepth:
    """Test market depth methods"""

    @patch('mymt5.symbol.mt5')
    def test_get_depth(self, mock_mt5, symbol):
        """Test getting market depth"""
        mock_depth_item = Mock()
        mock_depth_item.type = 1
        mock_depth_item.price = 1.09234
        mock_depth_item.volume = 100
        mock_depth_item.volume_real = 100.0

        mock_mt5.market_book_get.return_value = [mock_depth_item]
        mock_mt5.symbol_select.return_value = True

        result = symbol.get_depth('EURUSD')

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]['price'] == 1.09234

    @patch('mymt5.symbol.mt5')
    def test_get_depth_not_available(self, mock_mt5, symbol):
        """Test getting market depth when not available"""
        mock_mt5.market_book_get.return_value = None
        mock_mt5.symbol_select.return_value = True

        result = symbol.get_depth('EURUSD')

        assert result is None


class TestSubscriptions:
    """Test subscription methods"""

    @patch('mymt5.symbol.mt5')
    def test_subscribe(self, mock_mt5, symbol):
        """Test subscribing to market depth"""
        mock_mt5.market_book_add.return_value = True

        result = symbol.subscribe('EURUSD')

        assert result is True
        assert 'EURUSD' in symbol._subscriptions

    @patch('mymt5.symbol.mt5')
    def test_unsubscribe(self, mock_mt5, symbol):
        """Test unsubscribing from market depth"""
        symbol._subscriptions.add('EURUSD')
        mock_mt5.market_book_release.return_value = True

        result = symbol.unsubscribe('EURUSD')

        assert result is True
        assert 'EURUSD' not in symbol._subscriptions


class TestValidation:
    """Test validation methods"""

    @patch('mymt5.symbol.mt5')
    def test_validate_exists(self, mock_mt5, symbol, mock_symbol_info):
        """Test validating symbol exists"""
        mock_mt5.symbol_info.return_value = mock_symbol_info

        is_valid, message = symbol.validate('EURUSD', 'exists')

        assert is_valid is True
        assert message == "Symbol exists"

    @patch('mymt5.symbol.mt5')
    def test_validate_not_exists(self, mock_mt5, symbol):
        """Test validating symbol doesn't exist"""
        mock_mt5.symbol_info.return_value = None
        mock_mt5.last_error.return_value = (1, "Symbol not found")

        is_valid, message = symbol.validate('INVALID', 'exists')

        assert is_valid is False

    @patch('mymt5.symbol.mt5')
    def test_validate_tradable(self, mock_mt5, symbol, mock_symbol_info):
        """Test validating symbol is tradable"""
        mock_mt5.symbol_info.return_value = mock_symbol_info
        mock_symbol_info.trade_mode = 4

        is_valid, message = symbol.validate('EURUSD', 'tradable')

        assert is_valid is True

    @patch('mymt5.symbol.mt5')
    def test_validate_volume_valid(self, mock_mt5, symbol, mock_symbol_info):
        """Test validating valid volume"""
        mock_mt5.symbol_info.return_value = mock_symbol_info
        # Use 0.1 which aligns perfectly with step 0.01
        is_valid, message = symbol.validate('EURUSD', 'volume', volume=0.1)

        assert is_valid is True

    @patch('mymt5.symbol.mt5')
    def test_validate_volume_below_min(self, mock_mt5, symbol, mock_symbol_info):
        """Test validating volume below minimum"""
        mock_mt5.symbol_info.return_value = mock_symbol_info
        mock_symbol_info.volume_min = 0.01

        is_valid, message = symbol.validate_volume('EURUSD', 0.001)

        assert is_valid is False
        assert "below minimum" in message

    @patch('mymt5.symbol.mt5')
    def test_validate_volume_above_max(self, mock_mt5, symbol, mock_symbol_info):
        """Test validating volume above maximum"""
        mock_mt5.symbol_info.return_value = mock_symbol_info
        mock_symbol_info.volume_max = 100.0

        is_valid, message = symbol.validate_volume('EURUSD', 200.0)

        assert is_valid is False
        assert "above maximum" in message

    def test_validate_invalid_type(self, symbol):
        """Test invalid validation type raises ValueError"""
        with pytest.raises(ValueError):
            symbol.validate('EURUSD', 'invalid_type')


class TestUtility:
    """Test utility methods"""

    @patch('mymt5.symbol.mt5')
    def test_get_summary(self, mock_mt5, symbol, mock_symbol_info):
        """Test getting symbol summary"""
        mock_mt5.symbol_info.return_value = mock_symbol_info

        result = symbol.get_summary('EURUSD')

        assert isinstance(result, dict)
        assert result['name'] == 'EURUSD'
        assert result['bid'] == 1.09234
        assert result['ask'] == 1.09245
        assert 'description' in result

    @patch('mymt5.symbol.mt5')
    def test_export_list_dict(self, mock_mt5, symbol, mock_symbol_info):
        """Test exporting symbol list as dict"""
        mock_mt5.symbol_info.return_value = mock_symbol_info

        result = symbol.export_list(['EURUSD'], 'dict')

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]['name'] == 'EURUSD'

    @patch('mymt5.symbol.mt5')
    def test_export_list_json(self, mock_mt5, symbol, mock_symbol_info):
        """Test exporting symbol list as JSON"""
        mock_mt5.symbol_info.return_value = mock_symbol_info

        result = symbol.export_list(['EURUSD'], 'json')

        assert isinstance(result, str)
        assert 'EURUSD' in result

    def test_export_list_invalid_format(self, symbol):
        """Test invalid export format raises ValueError"""
        with pytest.raises(ValueError):
            symbol.export_list(['EURUSD'], 'invalid_format')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
