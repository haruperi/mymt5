"""Tests for MT5Account class"""

from mylogger import logger
import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
from mymt5.account import MT5Account


@pytest.fixture
def mock_client():
    """Create a mock MT5Client instance"""
    client = Mock()
    client.is_connected.return_value = True
    return client


@pytest.fixture
def mock_account_info():
    """Create mock account info"""
    account_info = Mock()
    account_info.login = 12345678
    account_info.trade_mode = 0  # Demo
    account_info.leverage = 100
    account_info.limit_orders = 200
    account_info.margin_so_mode = 0
    account_info.trade_allowed = True
    account_info.trade_expert = True
    account_info.margin_mode = 0
    account_info.currency_digits = 2
    account_info.fifo_close = False
    account_info.balance = 10000.0
    account_info.credit = 0.0
    account_info.profit = 500.0
    account_info.equity = 10500.0
    account_info.margin = 1000.0
    account_info.margin_free = 9500.0
    account_info.margin_level = 1050.0
    account_info.margin_so_call = 50.0
    account_info.margin_so_so = 30.0
    account_info.margin_initial = 0.0
    account_info.margin_maintenance = 0.0
    account_info.assets = 10500.0
    account_info.liabilities = 0.0
    account_info.commission_blocked = 0.0
    account_info.name = "Test Account"
    account_info.server = "TestServer-Demo"
    account_info.currency = "USD"
    account_info.company = "Test Broker"
    return account_info


@pytest.fixture
def account(mock_client):
    """Create MT5Account instance"""
    return MT5Account(mock_client)


class TestMT5AccountInit:
    """Test MT5Account initialization"""

    def test_init(self, mock_client):
        """Test account initialization"""
        account = MT5Account(mock_client)
        assert account.client == mock_client
        assert account._account_info_cache is None
        assert account._cache_timestamp is None
        assert account._cache_duration == 1


class TestMT5AccountGet:
    """Test MT5Account.get() method"""

    @patch('mymt5.account.mt5')
    def test_get_all_info(self, mock_mt5, account, mock_account_info):
        """Test getting all account information"""
        mock_mt5.account_info.return_value = mock_account_info

        result = account.get()

        assert isinstance(result, dict)
        assert result['login'] == 12345678
        assert result['balance'] == 10000.0
        assert result['equity'] == 10500.0
        assert result['currency'] == 'USD'

    @patch('mymt5.account.mt5')
    def test_get_specific_attribute(self, mock_mt5, account, mock_account_info):
        """Test getting specific account attribute"""
        mock_mt5.account_info.return_value = mock_account_info

        balance = account.get('balance')
        assert balance == 10000.0

        equity = account.get('equity')
        assert equity == 10500.0

    @patch('mymt5.account.mt5')
    def test_get_invalid_attribute(self, mock_mt5, account, mock_account_info):
        """Test getting invalid attribute raises ValueError"""
        mock_mt5.account_info.return_value = mock_account_info

        with pytest.raises(ValueError, match="does not exist"):
            account.get('invalid_attribute')

    @patch('mymt5.account.mt5')
    def test_get_caching(self, mock_mt5, account, mock_account_info):
        """Test that account info is cached"""
        mock_mt5.account_info.return_value = mock_account_info

        # First call should fetch from MT5
        result1 = account.get()
        assert mock_mt5.account_info.call_count == 1

        # Second call should use cache
        result2 = account.get()
        assert mock_mt5.account_info.call_count == 1  # Still 1
        assert result1 == result2

    @patch('mymt5.account.mt5')
    def test_get_cache_expiry(self, mock_mt5, account, mock_account_info):
        """Test that cache expires after duration"""
        mock_mt5.account_info.return_value = mock_account_info

        # Set very short cache duration
        account._cache_duration = 0

        # First call
        account.get()
        assert mock_mt5.account_info.call_count == 1

        # Second call should fetch again due to expired cache
        account.get()
        assert mock_mt5.account_info.call_count == 2


class TestMT5AccountFetchInfo:
    """Test MT5Account._fetch_account_info() method"""

    @patch('mymt5.account.mt5')
    def test_fetch_success(self, mock_mt5, account, mock_account_info):
        """Test successful fetch of account info"""
        mock_mt5.account_info.return_value = mock_account_info

        result = account._fetch_account_info()

        assert isinstance(result, dict)
        assert len(result) > 0
        assert result['login'] == 12345678

    @patch('mymt5.account.mt5')
    def test_fetch_failure(self, mock_mt5, account):
        """Test fetch failure raises RuntimeError"""
        mock_mt5.account_info.return_value = None
        mock_mt5.last_error.return_value = (1, "Test error")

        with pytest.raises(RuntimeError, match="Failed to get account info"):
            account._fetch_account_info()


class TestMT5AccountCheck:
    """Test MT5Account.check() method"""

    @patch('mymt5.account.mt5')
    def test_check_demo(self, mock_mt5, account, mock_account_info):
        """Test checking if account is demo"""
        mock_account_info.trade_mode = 0  # Demo
        mock_mt5.account_info.return_value = mock_account_info

        assert account.check('demo') is True

        mock_account_info.trade_mode = 2  # Real
        account._account_info_cache = None  # Clear cache
        assert account.check('demo') is False

    @patch('mymt5.account.mt5')
    def test_check_authorized(self, mock_mt5, account, mock_account_info):
        """Test checking if account is authorized"""
        mock_mt5.account_info.return_value = mock_account_info

        assert account.check('authorized') is True

    @patch('mymt5.account.mt5')
    def test_check_trade_allowed(self, mock_mt5, account, mock_account_info):
        """Test checking if trading is allowed"""
        mock_account_info.trade_allowed = True
        mock_mt5.account_info.return_value = mock_account_info

        assert account.check('trade_allowed') is True

        mock_account_info.trade_allowed = False
        account._account_info_cache = None  # Clear cache
        assert account.check('trade_allowed') is False

    @patch('mymt5.account.mt5')
    def test_check_expert_allowed(self, mock_mt5, account, mock_account_info):
        """Test checking if Expert Advisors are allowed"""
        mock_account_info.trade_expert = True
        mock_mt5.account_info.return_value = mock_account_info

        assert account.check('expert_allowed') is True

    def test_check_invalid_type(self, account):
        """Test invalid status type raises ValueError"""
        with pytest.raises(ValueError, match="Invalid status_type"):
            account.check('invalid_type')


class TestMT5AccountCalculate:
    """Test MT5Account.calculate() method"""

    @patch('mymt5.account.mt5')
    def test_calculate_margin_level(self, mock_mt5, account, mock_account_info):
        """Test calculating margin level"""
        mock_mt5.account_info.return_value = mock_account_info

        margin_level = account.calculate('margin_level')

        # equity / margin * 100 = 10500 / 1000 * 100 = 1050
        assert margin_level == 1050.0

    @patch('mymt5.account.mt5')
    def test_calculate_margin_level_zero_margin(self, mock_mt5, account, mock_account_info):
        """Test margin level with zero margin"""
        mock_account_info.margin = 0
        mock_mt5.account_info.return_value = mock_account_info

        margin_level = account.calculate('margin_level')
        assert margin_level == 0.0

    @patch('mymt5.account.mt5')
    def test_calculate_drawdown_percent(self, mock_mt5, account, mock_account_info):
        """Test calculating drawdown in percent"""
        mock_mt5.account_info.return_value = mock_account_info

        drawdown = account.calculate('drawdown', type='percent')

        # (balance - equity) / balance * 100 = (10000 - 10500) / 10000 * 100 = -5%
        assert drawdown == -5.0

    @patch('mymt5.account.mt5')
    def test_calculate_drawdown_absolute(self, mock_mt5, account, mock_account_info):
        """Test calculating drawdown in absolute"""
        mock_mt5.account_info.return_value = mock_account_info

        drawdown = account.calculate('drawdown', type='absolute')

        # balance - equity = 10000 - 10500 = -500
        assert drawdown == -500.0

    @patch('mymt5.account.mt5')
    def test_calculate_health(self, mock_mt5, account, mock_account_info):
        """Test calculating health metrics"""
        mock_mt5.account_info.return_value = mock_account_info

        health = account.calculate('health')

        assert isinstance(health, dict)
        assert 'balance' in health
        assert 'equity' in health
        assert 'margin_level' in health
        assert 'health_status' in health
        assert health['health_status'] == 'excellent'  # margin_level > 200

    @patch('mymt5.account.mt5')
    def test_calculate_margin_required(self, mock_mt5, account):
        """Test calculating required margin"""
        mock_symbol_info = Mock()
        mock_symbol_info.ask = 1.1000

        mock_mt5.symbol_info.return_value = mock_symbol_info
        mock_mt5.order_calc_margin.return_value = 1000.0
        mock_mt5.ORDER_TYPE_BUY = 0

        margin = account.calculate('margin_required', symbol='EURUSD', volume=1.0)

        assert margin == 1000.0
        mock_mt5.order_calc_margin.assert_called_once()

    def test_calculate_invalid_metric(self, account):
        """Test invalid metric raises ValueError"""
        with pytest.raises(ValueError, match="Invalid metric"):
            account.calculate('invalid_metric')


class TestMT5AccountValidateCredentials:
    """Test MT5Account.validate_credentials() method"""

    @patch('mymt5.account.mt5')
    def test_validate_valid_credentials(self, mock_mt5, account):
        """Test validating valid credentials"""
        mock_mt5.login.return_value = True

        result = account.validate_credentials(12345678, "password", "TestServer")

        assert result is True
        mock_mt5.login.assert_called_once_with(12345678, "password", "TestServer")

    @patch('mymt5.account.mt5')
    def test_validate_invalid_credentials(self, mock_mt5, account):
        """Test validating invalid credentials"""
        mock_mt5.login.return_value = False

        result = account.validate_credentials(12345678, "wrong_password", "TestServer")

        assert result is False

    @patch('mymt5.account.mt5')
    def test_validate_exception(self, mock_mt5, account):
        """Test validation with exception"""
        mock_mt5.login.side_effect = Exception("Connection error")

        result = account.validate_credentials(12345678, "password", "TestServer")

        assert result is False


class TestMT5AccountGetSummary:
    """Test MT5Account.get_summary() method"""

    @patch('mymt5.account.mt5')
    def test_get_summary(self, mock_mt5, account, mock_account_info):
        """Test getting account summary"""
        mock_mt5.account_info.return_value = mock_account_info

        summary = account.get_summary()

        assert isinstance(summary, dict)
        assert summary['login'] == 12345678
        assert summary['balance'] == 10000.0
        assert summary['equity'] == 10500.0
        assert summary['trade_mode'] == 'Demo'
        assert 'health_status' in summary


class TestMT5AccountExport:
    """Test MT5Account.export() method"""

    @patch('mymt5.account.mt5')
    def test_export_dict(self, mock_mt5, account, mock_account_info):
        """Test exporting as dict"""
        mock_mt5.account_info.return_value = mock_account_info

        result = account.export('dict')

        assert isinstance(result, dict)
        assert result['login'] == 12345678

    @patch('mymt5.account.mt5')
    def test_export_json_no_file(self, mock_mt5, account, mock_account_info):
        """Test exporting as JSON without file"""
        mock_mt5.account_info.return_value = mock_account_info

        result = account.export('json')

        assert isinstance(result, str)
        assert '12345678' in result

    @patch('mymt5.account.mt5')
    def test_export_json_with_file(self, mock_mt5, account, mock_account_info, tmp_path):
        """Test exporting as JSON with file"""
        mock_mt5.account_info.return_value = mock_account_info

        filepath = tmp_path / "account.json"
        result = account.export('json', str(filepath))

        assert "Exported to" in result
        assert filepath.exists()

    @patch('mymt5.account.mt5')
    def test_export_csv(self, mock_mt5, account, mock_account_info, tmp_path):
        """Test exporting as CSV"""
        mock_mt5.account_info.return_value = mock_account_info

        filepath = tmp_path / "account.csv"
        result = account.export('csv', str(filepath))

        assert "Exported to" in result
        assert filepath.exists()

    @patch('mymt5.account.mt5')
    def test_export_invalid_format(self, mock_mt5, account, mock_account_info):
        """Test invalid export format raises ValueError"""
        mock_mt5.account_info.return_value = mock_account_info

        with pytest.raises(ValueError, match="Invalid format"):
            account.export('invalid')


logger.info("test_account module loaded")
