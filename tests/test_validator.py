from mylogger import logger
"""
Unit tests for MT5Validator class.

Tests validation functionality for trading parameters including:
- Symbols, volumes, prices
- Stop loss and take profit levels
- Order types and parameters
- Timeframes and date ranges
- Trade requests and credentials
- Margin and tickets
- Batch validation
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import MetaTrader5 as mt5

from mymt5.validator import MT5Validator
from mymt5.enums import OrderType, TimeFrame


@pytest.fixture
def mock_mt5():
    """Mock MT5 functions."""
    with patch('mymt5.validator.mt5') as mock:
        # Mock symbol_info
        symbol_info = Mock()
        symbol_info.visible = True
        symbol_info.volume_min = 0.01
        symbol_info.volume_max = 100.0
        symbol_info.volume_step = 0.01
        symbol_info.trade_tick_size = 0.00001
        symbol_info.trade_stops_level = 10
        symbol_info.point = 0.00001
        mock.symbol_info.return_value = symbol_info
        mock.symbol_select.return_value = True

        # Mock account_info
        account_info = Mock()
        account_info.margin_free = 10000.0
        mock.account_info.return_value = account_info

        # Mock order type constants
        mock.ORDER_TYPE_BUY = 0
        mock.ORDER_TYPE_SELL = 1
        mock.ORDER_TYPE_BUY_LIMIT = 2
        mock.ORDER_TYPE_SELL_LIMIT = 3
        mock.ORDER_TYPE_BUY_STOP = 4
        mock.ORDER_TYPE_SELL_STOP = 5
        mock.ORDER_TYPE_BUY_STOP_LIMIT = 6
        mock.ORDER_TYPE_SELL_STOP_LIMIT = 7

        # Mock timeframe constants
        mock.TIMEFRAME_M1 = 1
        mock.TIMEFRAME_M5 = 5
        mock.TIMEFRAME_M15 = 15
        mock.TIMEFRAME_M30 = 30
        mock.TIMEFRAME_H1 = 60
        mock.TIMEFRAME_H4 = 240
        mock.TIMEFRAME_D1 = 1440
        mock.TIMEFRAME_W1 = 10080
        mock.TIMEFRAME_MN1 = 43200

        # Mock trade action constant
        mock.TRADE_ACTION_DEAL = 1

        yield mock


@pytest.fixture
def validator(mock_mt5):
    """Create MT5Validator instance."""
    return MT5Validator()


# Initialization Tests
class TestInitialization:
    """Test validator initialization."""

    def test_init_without_client(self, mock_mt5):
        """Test initialization without client."""
        validator = MT5Validator()
        assert validator.client is None
        assert validator._validation_rules is not None

    def test_init_with_client(self, mock_mt5):
        """Test initialization with client."""
        mock_client = Mock()
        validator = MT5Validator(client=mock_client)
        assert validator.client == mock_client

    def test_validation_rules_initialized(self, validator):
        """Test validation rules are properly initialized."""
        rules = validator._validation_rules
        assert 'volume' in rules
        assert 'price' in rules
        assert 'deviation' in rules
        assert 'magic' in rules


# Master Validate Method Tests
class TestMasterValidate:
    """Test master validate() method routing."""

    def test_validate_symbol(self, validator):
        """Test routing to symbol validation."""
        valid, msg = validator.validate('symbol', 'EURUSD')
        assert valid is True

    def test_validate_volume(self, validator):
        """Test routing to volume validation."""
        valid, msg = validator.validate('volume', 0.1, symbol='EURUSD')
        assert valid is True

    def test_validate_price(self, validator):
        """Test routing to price validation."""
        valid, msg = validator.validate('price', 1.1000, symbol='EURUSD')
        assert valid is True

    def test_validate_unknown_type(self, validator):
        """Test unknown validation type."""
        valid, msg = validator.validate('unknown_type', 'value')
        assert valid is False
        assert 'Unknown validation type' in msg

    def test_validate_exception_handling(self, validator):
        """Test exception handling in validate."""
        with patch.object(validator, '_validate_symbol', side_effect=Exception("Test error")):
            valid, msg = validator.validate('symbol', 'EURUSD')
            assert valid is False
            assert 'Test error' in msg


# Symbol Validation Tests
class TestSymbolValidation:
    """Test symbol validation."""

    def test_valid_symbol(self, validator):
        """Test valid symbol."""
        valid, msg = validator.validate('symbol', 'EURUSD')
        assert valid is True
        assert 'valid' in msg.lower()

    def test_empty_symbol(self, validator):
        """Test empty symbol."""
        valid, msg = validator.validate('symbol', '')
        assert valid is False
        assert 'non-empty string' in msg

    def test_none_symbol(self, validator):
        """Test None symbol."""
        valid, msg = validator.validate('symbol', None)
        assert valid is False
        assert 'non-empty string' in msg

    def test_symbol_not_found(self, validator, mock_mt5):
        """Test symbol not found."""
        mock_mt5.symbol_info.return_value = None
        valid, msg = validator.validate('symbol', 'INVALID')
        assert valid is False
        assert 'not found' in msg

    def test_symbol_not_visible(self, validator, mock_mt5):
        """Test symbol not visible."""
        symbol_info = Mock()
        symbol_info.visible = False
        mock_mt5.symbol_info.return_value = symbol_info
        mock_mt5.symbol_select.return_value = True

        valid, msg = validator.validate('symbol', 'HIDDEN')
        assert valid is True  # Should be valid after selection


# Volume Validation Tests
class TestVolumeValidation:
    """Test volume validation."""

    def test_valid_volume(self, validator):
        """Test valid volume."""
        valid, msg = validator.validate('volume', 0.1, symbol='EURUSD')
        assert valid is True

    def test_volume_not_number(self, validator):
        """Test volume is not a number."""
        valid, msg = validator.validate('volume', 'invalid')
        assert valid is False
        assert 'must be a number' in msg

    def test_volume_zero(self, validator):
        """Test volume is zero."""
        valid, msg = validator.validate('volume', 0)
        assert valid is False
        assert 'must be positive' in msg

    def test_volume_negative(self, validator):
        """Test volume is negative."""
        valid, msg = validator.validate('volume', -0.1)
        assert valid is False
        assert 'must be positive' in msg

    def test_volume_below_minimum(self, validator, mock_mt5):
        """Test volume below symbol minimum."""
        valid, msg = validator.validate('volume', 0.001, symbol='EURUSD')
        assert valid is False
        assert 'below minimum' in msg

    def test_volume_above_maximum(self, validator, mock_mt5):
        """Test volume above symbol maximum."""
        valid, msg = validator.validate('volume', 200.0, symbol='EURUSD')
        assert valid is False
        assert 'above maximum' in msg

    def test_volume_step_alignment(self, validator, mock_mt5):
        """Test volume step alignment."""
        # 0.015 is not aligned with step 0.01
        valid, msg = validator.validate('volume', 0.015, symbol='EURUSD')
        assert valid is False
        assert 'not aligned with step' in msg


# Price Validation Tests
class TestPriceValidation:
    """Test price validation."""

    def test_valid_price(self, validator):
        """Test valid price."""
        valid, msg = validator.validate('price', 1.1000, symbol='EURUSD')
        assert valid is True

    def test_price_not_number(self, validator):
        """Test price is not a number."""
        valid, msg = validator.validate('price', 'invalid')
        assert valid is False
        assert 'must be a number' in msg

    def test_price_zero(self, validator):
        """Test price is zero."""
        valid, msg = validator.validate('price', 0)
        assert valid is False
        assert 'must be positive' in msg

    def test_price_negative(self, validator):
        """Test price is negative."""
        valid, msg = validator.validate('price', -1.0)
        assert valid is False
        assert 'must be positive' in msg

    def test_price_outside_range(self, validator):
        """Test price outside valid range."""
        valid, msg = validator.validate('price', 2000000.0)
        assert valid is False
        assert 'outside valid range' in msg


# Stop Loss Validation Tests
class TestStopLossValidation:
    """Test stop loss validation."""

    def test_no_stop_loss(self, validator):
        """Test no stop loss (0)."""
        valid, msg = validator.validate('stop_loss', 0)
        assert valid is True
        assert 'No stop loss' in msg

    def test_valid_stop_loss_buy(self, validator, mock_mt5):
        """Test valid stop loss for buy order."""
        valid, msg = validator.validate(
            'stop_loss', 1.0900,
            entry_price=1.1000,
            order_type=mock_mt5.ORDER_TYPE_BUY,
            symbol='EURUSD'
        )
        assert valid is True

    def test_invalid_stop_loss_buy(self, validator, mock_mt5):
        """Test invalid stop loss for buy order (above entry)."""
        valid, msg = validator.validate(
            'stop_loss', 1.1100,
            entry_price=1.1000,
            order_type=mock_mt5.ORDER_TYPE_BUY,
            symbol='EURUSD'
        )
        assert valid is False
        assert 'below entry price' in msg

    def test_valid_stop_loss_sell(self, validator, mock_mt5):
        """Test valid stop loss for sell order."""
        valid, msg = validator.validate(
            'stop_loss', 1.1100,
            entry_price=1.1000,
            order_type=mock_mt5.ORDER_TYPE_SELL,
            symbol='EURUSD'
        )
        assert valid is True

    def test_invalid_stop_loss_sell(self, validator, mock_mt5):
        """Test invalid stop loss for sell order (below entry)."""
        valid, msg = validator.validate(
            'stop_loss', 1.0900,
            entry_price=1.1000,
            order_type=mock_mt5.ORDER_TYPE_SELL,
            symbol='EURUSD'
        )
        assert valid is False
        assert 'above entry price' in msg

    def test_stop_loss_too_close(self, validator, mock_mt5):
        """Test stop loss too close to entry."""
        # trade_stops_level is 10, point is 0.00001, so min distance is 0.0001
        valid, msg = validator.validate(
            'stop_loss', 1.09999,
            entry_price=1.1000,
            order_type=mock_mt5.ORDER_TYPE_BUY,
            symbol='EURUSD'
        )
        assert valid is False
        assert 'too close to entry' in msg


# Take Profit Validation Tests
class TestTakeProfitValidation:
    """Test take profit validation."""

    def test_no_take_profit(self, validator):
        """Test no take profit (0)."""
        valid, msg = validator.validate('take_profit', 0)
        assert valid is True
        assert 'No take profit' in msg

    def test_valid_take_profit_buy(self, validator, mock_mt5):
        """Test valid take profit for buy order."""
        valid, msg = validator.validate(
            'take_profit', 1.1100,
            entry_price=1.1000,
            order_type=mock_mt5.ORDER_TYPE_BUY,
            symbol='EURUSD'
        )
        assert valid is True

    def test_invalid_take_profit_buy(self, validator, mock_mt5):
        """Test invalid take profit for buy order (below entry)."""
        valid, msg = validator.validate(
            'take_profit', 1.0900,
            entry_price=1.1000,
            order_type=mock_mt5.ORDER_TYPE_BUY,
            symbol='EURUSD'
        )
        assert valid is False
        assert 'above entry price' in msg

    def test_valid_take_profit_sell(self, validator, mock_mt5):
        """Test valid take profit for sell order."""
        valid, msg = validator.validate(
            'take_profit', 1.0900,
            entry_price=1.1000,
            order_type=mock_mt5.ORDER_TYPE_SELL,
            symbol='EURUSD'
        )
        assert valid is True

    def test_invalid_take_profit_sell(self, validator, mock_mt5):
        """Test invalid take profit for sell order (above entry)."""
        valid, msg = validator.validate(
            'take_profit', 1.1100,
            entry_price=1.1000,
            order_type=mock_mt5.ORDER_TYPE_SELL,
            symbol='EURUSD'
        )
        assert valid is False
        assert 'below entry price' in msg


# Order Type Validation Tests
class TestOrderTypeValidation:
    """Test order type validation."""

    def test_valid_order_type_string(self, validator):
        """Test valid order type string."""
        valid, msg = validator.validate('order_type', 'BUY')
        assert valid is True

    def test_valid_order_type_int(self, validator, mock_mt5):
        """Test valid order type constant."""
        valid, msg = validator.validate('order_type', mock_mt5.ORDER_TYPE_BUY)
        assert valid is True

    def test_invalid_order_type_string(self, validator):
        """Test invalid order type string."""
        valid, msg = validator.validate('order_type', 'INVALID')
        assert valid is False
        assert 'Invalid order type string' in msg

    def test_invalid_order_type_int(self, validator):
        """Test invalid order type constant."""
        valid, msg = validator.validate('order_type', 999)
        assert valid is False
        assert 'Invalid order type constant' in msg

    def test_invalid_order_type_type(self, validator):
        """Test invalid order type type."""
        valid, msg = validator.validate('order_type', [])
        assert valid is False
        assert 'must be string or integer' in msg


# Magic Number Validation Tests
class TestMagicValidation:
    """Test magic number validation."""

    def test_valid_magic(self, validator):
        """Test valid magic number."""
        valid, msg = validator.validate('magic', 12345)
        assert valid is True

    def test_magic_not_int(self, validator):
        """Test magic is not an integer."""
        valid, msg = validator.validate('magic', 12345.5)
        assert valid is False
        assert 'must be an integer' in msg

    def test_magic_below_range(self, validator):
        """Test magic below valid range."""
        valid, msg = validator.validate('magic', -1)
        assert valid is False
        assert 'outside valid range' in msg

    def test_magic_above_range(self, validator):
        """Test magic above valid range."""
        valid, msg = validator.validate('magic', 2147483648)
        assert valid is False
        assert 'outside valid range' in msg


# Deviation Validation Tests
class TestDeviationValidation:
    """Test deviation validation."""

    def test_valid_deviation(self, validator):
        """Test valid deviation."""
        valid, msg = validator.validate('deviation', 10)
        assert valid is True

    def test_deviation_not_int(self, validator):
        """Test deviation is not an integer."""
        valid, msg = validator.validate('deviation', 10.5)
        assert valid is False
        assert 'must be an integer' in msg

    def test_deviation_below_range(self, validator):
        """Test deviation below valid range."""
        valid, msg = validator.validate('deviation', -1)
        assert valid is False
        assert 'outside valid range' in msg

    def test_deviation_above_range(self, validator):
        """Test deviation above valid range."""
        valid, msg = validator.validate('deviation', 101)
        assert valid is False
        assert 'outside valid range' in msg


# Expiration Validation Tests
class TestExpirationValidation:
    """Test expiration validation."""

    def test_valid_expiration(self, validator):
        """Test valid expiration."""
        future_time = datetime.now() + timedelta(hours=1)
        valid, msg = validator.validate('expiration', future_time)
        assert valid is True

    def test_expiration_not_datetime(self, validator):
        """Test expiration is not a datetime."""
        valid, msg = validator.validate('expiration', 'invalid')
        assert valid is False
        assert 'must be a datetime object' in msg

    def test_expiration_in_past(self, validator):
        """Test expiration in the past."""
        past_time = datetime.now() - timedelta(hours=1)
        valid, msg = validator.validate('expiration', past_time)
        assert valid is False
        assert 'must be in the future' in msg

    def test_expiration_too_far(self, validator):
        """Test expiration too far in future."""
        far_future = datetime.now() + timedelta(days=400)
        valid, msg = validator.validate('expiration', far_future)
        assert valid is False
        assert 'too far in the future' in msg


# Timeframe Validation Tests
class TestTimeframeValidation:
    """Test timeframe validation."""

    def test_valid_timeframe_enum(self, validator):
        """Test valid timeframe enum."""
        valid, msg = validator.validate('timeframe', TimeFrame.M1)
        assert valid is True

    def test_valid_timeframe_string(self, validator):
        """Test valid timeframe string."""
        valid, msg = validator.validate('timeframe', 'M1')
        assert valid is True

    def test_valid_timeframe_int(self, validator, mock_mt5):
        """Test valid timeframe constant."""
        valid, msg = validator.validate('timeframe', mock_mt5.TIMEFRAME_M1)
        assert valid is True

    def test_invalid_timeframe_string(self, validator):
        """Test invalid timeframe string."""
        valid, msg = validator.validate('timeframe', 'INVALID')
        assert valid is False
        assert 'Invalid timeframe string' in msg

    def test_invalid_timeframe_int(self, validator):
        """Test invalid timeframe constant."""
        valid, msg = validator.validate('timeframe', 999)
        assert valid is False
        assert 'Invalid timeframe constant' in msg


# Date Range Validation Tests
class TestDateRangeValidation:
    """Test date range validation."""

    def test_valid_date_range(self, validator):
        """Test valid date range."""
        start = datetime.now() - timedelta(days=30)
        end = datetime.now() - timedelta(days=1)
        valid, msg = validator.validate('date_range', start, end_date=end)
        assert valid is True

    def test_start_not_datetime(self, validator):
        """Test start date is not a datetime."""
        valid, msg = validator.validate('date_range', 'invalid')
        assert valid is False
        assert 'must be a datetime object' in msg

    def test_start_too_far_past(self, validator):
        """Test start date too far in past."""
        start = datetime.now() - timedelta(days=4000)
        valid, msg = validator.validate('date_range', start)
        assert valid is False
        assert 'too far in the past' in msg

    def test_end_not_datetime(self, validator):
        """Test end date is not a datetime."""
        start = datetime.now() - timedelta(days=30)
        valid, msg = validator.validate('date_range', start, end_date='invalid')
        assert valid is False
        assert 'must be a datetime object' in msg

    def test_end_before_start(self, validator):
        """Test end date before start date."""
        start = datetime.now() - timedelta(days=1)
        end = datetime.now() - timedelta(days=30)
        valid, msg = validator.validate('date_range', start, end_date=end)
        assert valid is False
        assert 'must be after start date' in msg

    def test_end_in_future(self, validator):
        """Test end date in future."""
        start = datetime.now() - timedelta(days=30)
        end = datetime.now() + timedelta(days=1)
        valid, msg = validator.validate('date_range', start, end_date=end)
        assert valid is False
        assert 'cannot be in the future' in msg


# Trade Request Validation Tests
class TestTradeRequestValidation:
    """Test trade request validation."""

    def test_valid_trade_request(self, validator, mock_mt5):
        """Test valid trade request."""
        request = {
            'action': mock_mt5.TRADE_ACTION_DEAL,
            'symbol': 'EURUSD',
            'volume': 0.1,
            'type': mock_mt5.ORDER_TYPE_BUY,
            'price': 1.1000,
            'sl': 1.0900,
            'tp': 1.1100,
            'magic': 12345,
            'deviation': 10
        }
        valid, msg = validator.validate('trade_request', request)
        assert valid is True

    def test_missing_required_field(self, validator):
        """Test missing required field."""
        request = {
            'action': 1,
            'symbol': 'EURUSD',
            # Missing volume and type
        }
        valid, msg = validator.validate('trade_request', request)
        assert valid is False
        assert 'Missing required field' in msg

    def test_invalid_symbol_in_request(self, validator, mock_mt5):
        """Test invalid symbol in request."""
        mock_mt5.symbol_info.return_value = None
        request = {
            'action': 1,
            'symbol': 'INVALID',
            'volume': 0.1,
            'type': 0
        }
        valid, msg = validator.validate('trade_request', request)
        assert valid is False
        assert 'Invalid symbol' in msg

    def test_invalid_volume_in_request(self, validator, mock_mt5):
        """Test invalid volume in request."""
        request = {
            'action': 1,
            'symbol': 'EURUSD',
            'volume': -0.1,
            'type': 0
        }
        valid, msg = validator.validate('trade_request', request)
        assert valid is False
        assert 'Invalid volume' in msg


# Credentials Validation Tests
class TestCredentialsValidation:
    """Test credentials validation."""

    def test_valid_credentials(self, validator):
        """Test valid credentials."""
        credentials = {
            'login': 12345678,
            'password': 'password123',
            'server': 'MetaQuotes-Demo'
        }
        valid, msg = validator.validate('credentials', credentials)
        assert valid is True

    def test_missing_credential_field(self, validator):
        """Test missing credential field."""
        credentials = {
            'login': 12345678,
            'password': 'password123'
            # Missing server
        }
        valid, msg = validator.validate('credentials', credentials)
        assert valid is False
        assert 'Missing credential field' in msg

    def test_invalid_login(self, validator):
        """Test invalid login."""
        credentials = {
            'login': -12345,
            'password': 'password123',
            'server': 'MetaQuotes-Demo'
        }
        valid, msg = validator.validate('credentials', credentials)
        assert valid is False
        assert 'Login must be a positive integer' in msg

    def test_empty_password(self, validator):
        """Test empty password."""
        credentials = {
            'login': 12345678,
            'password': '',
            'server': 'MetaQuotes-Demo'
        }
        valid, msg = validator.validate('credentials', credentials)
        assert valid is False
        assert 'Password must be a non-empty string' in msg

    def test_empty_server(self, validator):
        """Test empty server."""
        credentials = {
            'login': 12345678,
            'password': 'password123',
            'server': ''
        }
        valid, msg = validator.validate('credentials', credentials)
        assert valid is False
        assert 'Server must be a non-empty string' in msg


# Margin Validation Tests
class TestMarginValidation:
    """Test margin validation."""

    def test_valid_margin(self, validator, mock_mt5):
        """Test valid margin (sufficient)."""
        valid, msg = validator.validate('margin', 5000.0)
        assert valid is True
        assert 'Sufficient margin' in msg

    def test_margin_not_number(self, validator):
        """Test margin is not a number."""
        valid, msg = validator.validate('margin', 'invalid')
        assert valid is False
        assert 'must be a number' in msg

    def test_margin_negative(self, validator):
        """Test margin is negative."""
        valid, msg = validator.validate('margin', -100.0)
        assert valid is False
        assert 'cannot be negative' in msg

    def test_insufficient_margin(self, validator, mock_mt5):
        """Test insufficient margin."""
        valid, msg = validator.validate('margin', 15000.0)
        assert valid is False
        assert 'Insufficient margin' in msg

    def test_margin_no_account_info(self, validator, mock_mt5):
        """Test margin validation with no account info."""
        mock_mt5.account_info.return_value = None
        valid, msg = validator.validate('margin', 5000.0)
        assert valid is False
        assert 'Cannot get account information' in msg


# Ticket Validation Tests
class TestTicketValidation:
    """Test ticket validation."""

    def test_valid_ticket(self, validator):
        """Test valid ticket."""
        valid, msg = validator.validate('ticket', 12345)
        assert valid is True

    def test_ticket_not_int(self, validator):
        """Test ticket is not an integer."""
        valid, msg = validator.validate('ticket', 12345.5)
        assert valid is False
        assert 'must be an integer' in msg

    def test_ticket_zero(self, validator):
        """Test ticket is zero."""
        valid, msg = validator.validate('ticket', 0)
        assert valid is False
        assert 'must be positive' in msg

    def test_ticket_negative(self, validator):
        """Test ticket is negative."""
        valid, msg = validator.validate('ticket', -12345)
        assert valid is False
        assert 'must be positive' in msg


# Batch Validation Tests
class TestBatchValidation:
    """Test batch validation."""

    def test_validate_multiple_all_valid(self, validator):
        """Test batch validation with all valid."""
        validations = [
            {'type': 'symbol', 'value': 'EURUSD'},
            {'type': 'volume', 'value': 0.1, 'symbol': 'EURUSD'},
            {'type': 'price', 'value': 1.1000},
            {'type': 'magic', 'value': 12345}
        ]
        all_valid, errors = validator.validate_multiple(validations)
        assert all_valid is True
        assert len(errors) == 0

    def test_validate_multiple_some_invalid(self, validator):
        """Test batch validation with some invalid."""
        validations = [
            {'type': 'symbol', 'value': 'EURUSD'},
            {'type': 'volume', 'value': -0.1},  # Invalid
            {'type': 'price', 'value': 1.1000},
            {'type': 'magic', 'value': -1}  # Invalid
        ]
        all_valid, errors = validator.validate_multiple(validations)
        assert all_valid is False
        assert len(errors) == 2

    def test_validate_multiple_missing_type(self, validator):
        """Test batch validation with missing type."""
        validations = [
            {'value': 'EURUSD'}  # Missing type
        ]
        all_valid, errors = validator.validate_multiple(validations)
        assert all_valid is False
        assert len(errors) == 1
        assert 'Missing type' in errors[0]

    def test_validate_multiple_missing_value(self, validator):
        """Test batch validation with missing value."""
        validations = [
            {'type': 'symbol'}  # Missing value
        ]
        all_valid, errors = validator.validate_multiple(validations)
        assert all_valid is False
        assert len(errors) == 1
        assert 'Missing value' in errors[0]

    def test_validate_multiple_empty_list(self, validator):
        """Test batch validation with empty list."""
        all_valid, errors = validator.validate_multiple([])
        assert all_valid is True
        assert len(errors) == 0


# Validation Rules Management Tests
class TestValidationRules:
    """Test validation rules management."""

    def test_get_validation_rules(self, validator):
        """Test getting validation rules."""
        rules = validator.get_validation_rules()
        assert isinstance(rules, dict)
        assert 'volume' in rules
        assert 'price' in rules
        assert 'deviation' in rules
        assert 'magic' in rules

    def test_get_validation_rules_returns_copy(self, validator):
        """Test that get_validation_rules returns a copy."""
        rules1 = validator.get_validation_rules()
        rules2 = validator.get_validation_rules()
        assert rules1 is not rules2
        assert rules1 == rules2

    def test_update_validation_rule(self, validator):
        """Test updating validation rule."""
        validator.update_validation_rule('volume', 'min', 0.001)
        rules = validator.get_validation_rules()
        assert rules['volume']['min'] == 0.001

    def test_update_validation_rule_invalid_type(self, validator):
        """Test updating validation rule with invalid type."""
        original_rules = validator.get_validation_rules()
        validator.update_validation_rule('invalid_type', 'min', 0.001)
        # Should not change anything
        assert validator.get_validation_rules() == original_rules

    def test_update_validation_rule_invalid_name(self, validator):
        """Test updating validation rule with invalid name."""
        original_min = validator.get_validation_rules()['volume']['min']
        validator.update_validation_rule('volume', 'invalid_name', 0.001)
        # Should not change anything
        assert validator.get_validation_rules()['volume']['min'] == original_min


# Edge Cases and Error Handling Tests
class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_validate_with_exception(self, validator):
        """Test validation with exception."""
        with patch.object(validator, '_validate_symbol', side_effect=Exception("Test error")):
            valid, msg = validator.validate('symbol', 'EURUSD')
            assert valid is False

    def test_validate_multiple_with_exception(self, validator):
        """Test batch validation with exception."""
        with patch.object(validator, 'validate', side_effect=Exception("Test error")):
            all_valid, errors = validator.validate_multiple([
                {'type': 'symbol', 'value': 'EURUSD'}
            ])
            assert all_valid is False
            assert len(errors) > 0

    def test_order_type_string_conversion(self, validator, mock_mt5):
        """Test order type string conversion in SL/TP validation."""
        valid, msg = validator.validate(
            'stop_loss', 1.0900,
            entry_price=1.1000,
            order_type='BUY',  # String instead of int
            symbol='EURUSD'
        )
        assert valid is True

    def test_invalid_order_type_string_in_sl_validation(self, validator):
        """Test invalid order type string in SL validation."""
        valid, msg = validator.validate(
            'stop_loss', 1.0900,
            entry_price=1.1000,
            order_type='INVALID',
            symbol='EURUSD'
        )
        assert valid is False
        assert 'Invalid order type' in msg
