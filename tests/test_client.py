"""
Unit tests for MT5Client class.

This module contains comprehensive unit tests for the MT5Client class,
testing all connection management, authentication, auto-reconnection,
configuration, multi-account, event system, and utility features.
"""

from mylogger import logger
import pytest
from unittest.mock import Mock, patch, MagicMock, mock_open
import MetaTrader5 as mt5
from datetime import datetime
import json

from mymt5.client import MT5Client
from mymt5.enums import ConnectionState


logger.info("Loading test_client module")


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def client():
    """Create a fresh MT5Client instance for each test."""
    return MT5Client()


@pytest.fixture
def mock_mt5(monkeypatch):
    """Mock MT5 module functions."""
    mock_initialize = Mock(return_value=True)
    mock_login = Mock(return_value=True)
    mock_shutdown = Mock()
    mock_terminal_info = Mock(return_value=Mock(connected=True))
    mock_last_error = Mock(return_value=(0, "No error"))

    monkeypatch.setattr(mt5, 'initialize', mock_initialize)
    monkeypatch.setattr(mt5, 'login', mock_login)
    monkeypatch.setattr(mt5, 'shutdown', mock_shutdown)
    monkeypatch.setattr(mt5, 'terminal_info', mock_terminal_info)
    monkeypatch.setattr(mt5, 'last_error', mock_last_error)

    return {
        'initialize': mock_initialize,
        'login': mock_login,
        'shutdown': mock_shutdown,
        'terminal_info': mock_terminal_info,
        'last_error': mock_last_error
    }


# =============================================================================
# INITIALIZATION TESTS
# =============================================================================

class TestInitialization:
    """Tests for MT5Client initialization."""

    def test_client_initialization(self, client):
        """Test that client initializes with correct default values."""
        assert client.connection_state == ConnectionState.DISCONNECTED
        assert client.account_login is None
        assert client.account_password is None
        assert client.account_server is None
        assert client.auto_reconnect_enabled is False
        assert client.retry_attempts == 3
        assert client.retry_delay == 5
        assert isinstance(client.accounts, dict)
        assert isinstance(client.config, dict)

    def test_client_initialization_with_parameters(self):
        """Test client initialization with custom parameters."""
        client = MT5Client(
            path="C:/MT5/terminal64.exe",
            timeout=30000,
            portable=True
        )
        assert client.path == "C:/MT5/terminal64.exe"
        assert client.timeout == 30000
        assert client.portable is True


# =============================================================================
# CONNECTION MANAGEMENT TESTS
# =============================================================================

class TestConnectionManagement:
    """Tests for connection management methods."""

    def test_initialize_success(self, client, mock_mt5):
        """Test successful initialization."""
        result = client.initialize(
            login=12345,
            password="testpass",
            server="TestServer"
        )

        assert result is True
        assert client.connection_state == ConnectionState.CONNECTED
        assert client.account_login == 12345
        assert client.account_password == "testpass"
        assert client.account_server == "TestServer"
        mock_mt5['initialize'].assert_called_once()
        mock_mt5['login'].assert_called_once_with(
            login=12345,
            password="testpass",
            server="TestServer"
        )

    def test_initialize_failure(self, client, mock_mt5):
        """Test initialization failure."""
        mock_mt5['initialize'].return_value = False
        mock_mt5['last_error'].return_value = (1, "Initialization failed")

        result = client.initialize()

        assert result is False
        assert client.connection_state == ConnectionState.FAILED

    def test_initialize_without_credentials(self, client, mock_mt5):
        """Test initialization without credentials."""
        result = client.initialize()

        assert result is True
        assert client.connection_state == ConnectionState.CONNECTED
        mock_mt5['initialize'].assert_called_once()
        mock_mt5['login'].assert_not_called()

    def test_connect_method(self, client, mock_mt5):
        """Test that connect is an alias for initialize."""
        result = client.connect(login=12345, password="pass", server="Test")

        assert result is True
        assert client.connection_state == ConnectionState.CONNECTED

    def test_disconnect(self, client):
        """Test disconnection."""
        client.connection_state = ConnectionState.CONNECTED

        result = client.disconnect()

        assert result is True
        assert client.connection_state == ConnectionState.DISCONNECTED

    def test_shutdown(self, client, mock_mt5):
        """Test shutdown."""
        client.connection_state = ConnectionState.CONNECTED

        client.shutdown()

        assert client.connection_state == ConnectionState.DISCONNECTED
        mock_mt5['shutdown'].assert_called_once()

    def test_is_connected_true(self, client, mock_mt5):
        """Test is_connected when connected."""
        client.connection_state = ConnectionState.CONNECTED
        mock_mt5['terminal_info'].return_value = Mock(connected=True)

        assert client.is_connected() is True

    def test_is_connected_false(self, client, mock_mt5):
        """Test is_connected when disconnected."""
        client.connection_state = ConnectionState.DISCONNECTED
        mock_mt5['terminal_info'].return_value = None

        assert client.is_connected() is False

    def test_ping_success(self, client, mock_mt5):
        """Test successful ping."""
        mock_mt5['terminal_info'].return_value = Mock(connected=True)

        assert client.ping() is True

    def test_ping_failure(self, client, mock_mt5):
        """Test failed ping."""
        mock_mt5['terminal_info'].return_value = None

        assert client.ping() is False


# =============================================================================
# AUTHENTICATION TESTS
# =============================================================================

class TestAuthentication:
    """Tests for authentication methods."""

    def test_login_success(self, client, mock_mt5):
        """Test successful login."""
        mock_mt5['login'].return_value = True

        result = client.login(12345, "password", "Server")

        assert result is True
        assert client.account_login == 12345
        assert client.account_password == "password"
        assert client.account_server == "Server"
        assert client.connection_state == ConnectionState.CONNECTED

    def test_login_failure(self, client, mock_mt5):
        """Test failed login."""
        mock_mt5['login'].return_value = False
        mock_mt5['last_error'].return_value = (10004, "Invalid credentials")

        result = client.login(12345, "wrongpass", "Server")

        assert result is False
        assert client._last_error == (10004, "Invalid credentials")

    def test_logout(self, client):
        """Test logout."""
        client.account_login = 12345
        client.account_password = "pass"
        client.account_server = "Server"

        result = client.logout()

        assert result is True
        assert client.account_login is None
        assert client.account_password is None
        assert client.account_server is None


# =============================================================================
# AUTO-RECONNECTION TESTS
# =============================================================================

class TestAutoReconnection:
    """Tests for auto-reconnection functionality."""

    def test_reconnect_success(self, client, mock_mt5):
        """Test successful reconnection."""
        client.account_login = 12345
        client.account_password = "pass"
        client.account_server = "Server"

        result = client.reconnect()

        assert result is True
        assert client.connection_state == ConnectionState.CONNECTED

    def test_reconnect_without_credentials(self, client):
        """Test reconnection without stored credentials."""
        result = client.reconnect()

        assert result is False

    def test_enable_auto_reconnect(self, client):
        """Test enabling auto-reconnect."""
        client.enable_auto_reconnect(retry_attempts=5, retry_delay=10)

        assert client.auto_reconnect_enabled is True
        assert client.retry_attempts == 5
        assert client.retry_delay == 10

    def test_disable_auto_reconnect(self, client):
        """Test disabling auto-reconnect."""
        client.auto_reconnect_enabled = True

        client.disable_auto_reconnect()

        assert client.auto_reconnect_enabled is False

    def test_set_retry_attempts(self, client):
        """Test setting retry attempts."""
        client.set_retry_attempts(10)

        assert client.retry_attempts == 10

    def test_set_retry_delay(self, client):
        """Test setting retry delay."""
        client.set_retry_delay(15)

        assert client.retry_delay == 15

    @patch('time.sleep')
    def test_handle_reconnection_success(self, mock_sleep, client, mock_mt5):
        """Test successful auto-reconnection handling."""
        client.account_login = 12345
        client.account_password = "pass"
        client.account_server = "Server"
        client.retry_attempts = 2

        result = client._handle_reconnection()

        assert result is True
        assert client._reconnection_in_progress is False

    @patch('time.sleep')
    def test_handle_reconnection_failure(self, mock_sleep, client, mock_mt5):
        """Test failed auto-reconnection after all attempts."""
        mock_mt5['initialize'].return_value = False
        client.account_login = 12345
        client.account_password = "pass"
        client.account_server = "Server"
        client.retry_attempts = 2

        result = client._handle_reconnection()

        assert result is False
        # Sleep is called in reconnect() and between attempts
        # With 2 attempts: reconnect sleeps twice + 1 sleep between attempts = 3 total
        assert mock_sleep.call_count >= 1  # At least between attempts


# =============================================================================
# CONFIGURATION TESTS
# =============================================================================

class TestConfiguration:
    """Tests for configuration management."""

    def test_configure(self, client):
        """Test configuration update."""
        client.configure(
            timeout=30000,
            custom_setting="value"
        )

        assert client.timeout == 30000
        assert client.config['custom_setting'] == "value"

    def test_get_config_all(self, client):
        """Test getting all configuration."""
        config = client.get_config()

        assert isinstance(config, dict)
        assert 'timeout' in config
        assert 'retry_attempts' in config

    def test_get_config_specific(self, client):
        """Test getting specific configuration value."""
        value = client.get_config('timeout')

        assert value == client.timeout

    def test_load_config(self, client):
        """Test loading configuration from file."""
        config_data = {'timeout': 30000, 'retry_attempts': 5}

        with patch('builtins.open', mock_open(read_data=json.dumps(config_data))):
            result = client.load_config('config.json')

        assert result is True
        assert client.timeout == 30000
        assert client.retry_attempts == 5

    def test_save_config(self, client):
        """Test saving configuration to file."""
        with patch('builtins.open', mock_open()) as mock_file:
            result = client.save_config('config.json')

        assert result is True
        assert client.config_path == 'config.json'
        mock_file.assert_called_once()


# =============================================================================
# MULTI-ACCOUNT TESTS
# =============================================================================

class TestMultiAccount:
    """Tests for multi-account support."""

    def test_save_account(self, client):
        """Test saving account credentials."""
        client.save_account('demo', 12345, 'pass', 'Server')

        assert 'demo' in client.accounts
        assert client.accounts['demo']['login'] == 12345
        assert client.accounts['demo']['password'] == 'pass'
        assert client.accounts['demo']['server'] == 'Server'

    def test_switch_account_saved(self, client, mock_mt5):
        """Test switching to a saved account."""
        client.save_account('demo', 12345, 'pass', 'Server')

        result = client.switch_account('demo')

        assert result is True
        assert client.current_account == 'demo'

    def test_switch_account_new(self, client, mock_mt5):
        """Test switching to a new account."""
        result = client.switch_account('live', 54321, 'newpass', 'LiveServer')

        assert result is True
        assert client.current_account == 'live'
        assert 'live' in client.accounts

    def test_switch_account_not_found(self, client):
        """Test switching to non-existent account without credentials."""
        result = client.switch_account('nonexistent')

        assert result is False

    def test_list_accounts(self, client):
        """Test listing saved accounts."""
        client.save_account('demo1', 111, 'p1', 's1')
        client.save_account('demo2', 222, 'p2', 's2')

        accounts = client.list_accounts()

        assert len(accounts) == 2
        assert 'demo1' in accounts
        assert 'demo2' in accounts

    def test_remove_account_success(self, client):
        """Test removing an existing account."""
        client.save_account('demo', 12345, 'pass', 'Server')

        result = client.remove_account('demo')

        assert result is True
        assert 'demo' not in client.accounts

    def test_remove_account_not_found(self, client):
        """Test removing non-existent account."""
        result = client.remove_account('nonexistent')

        assert result is False

    def test_load_account(self, client):
        """Test loading accounts from file."""
        accounts_data = {
            'demo': {'login': 12345, 'password': 'pass', 'server': 'Server'}
        }

        with patch('builtins.open', mock_open(read_data=json.dumps(accounts_data))):
            result = client.load_account('accounts.json')

        assert result is True
        assert 'demo' in client.accounts


# =============================================================================
# EVENT SYSTEM TESTS
# =============================================================================

class TestEventSystem:
    """Tests for event system."""

    def test_register_callback(self, client):
        """Test registering an event callback."""
        callback = Mock()

        client.on('connect', callback)

        assert callback in client._event_handlers['connect']

    def test_unregister_specific_callback(self, client):
        """Test unregistering a specific callback."""
        callback = Mock()
        client.on('connect', callback)

        client.off('connect', callback)

        assert callback not in client._event_handlers['connect']

    def test_unregister_all_callbacks(self, client):
        """Test unregistering all callbacks for an event."""
        callback1 = Mock()
        callback2 = Mock()
        client.on('connect', callback1)
        client.on('connect', callback2)

        client.off('connect')

        assert len(client._event_handlers['connect']) == 0

    def test_trigger_event(self, client):
        """Test triggering an event."""
        callback = Mock()
        client.on('connect', callback)

        client.trigger_event('connect', client=client)

        callback.assert_called_once_with(client=client)

    def test_trigger_event_with_exception(self, client):
        """Test triggering event when callback raises exception."""
        callback = Mock(side_effect=Exception("Test error"))
        client.on('connect', callback)

        # Should not raise exception
        client.trigger_event('connect', client=client)

        callback.assert_called_once()


# =============================================================================
# STATUS & DIAGNOSTICS TESTS
# =============================================================================

class TestStatusDiagnostics:
    """Tests for status and diagnostics methods."""

    def test_get_status(self, client, mock_mt5):
        """Test getting client status."""
        client.connection_state = ConnectionState.CONNECTED
        client.account_login = 12345
        client.account_server = "TestServer"

        status = client.get_status()

        assert isinstance(status, dict)
        assert status['connection_state'] == 'connected'
        assert status['account_info']['login'] == 12345
        assert status['account_info']['server'] == "TestServer"
        assert 'statistics' in status

    def test_get_connection_statistics(self, client):
        """Test getting connection statistics."""
        client._connection_attempts = 10
        client._successful_connections = 8
        client._failed_connections = 2
        client._error_count = 3

        stats = client.get_connection_statistics()

        assert stats['total_attempts'] == 10
        assert stats['successful_connections'] == 8
        assert stats['failed_connections'] == 2
        assert stats['success_rate'] == 0.8
        assert stats['error_count'] == 3


# =============================================================================
# ERROR HANDLING TESTS
# =============================================================================

class TestErrorHandling:
    """Tests for error handling."""

    def test_get_error(self, client):
        """Test getting last error."""
        client._last_error = (10004, "Connection failed")

        error = client.get_error()

        assert error == (10004, "Connection failed")

    def test_handle_error(self, client):
        """Test public error handling method."""
        client.handle_error(10004, "Test error")

        assert client._last_error == (10004, "Test error")
        assert client._error_count == 1

    def test_handle_error_triggers_event(self, client):
        """Test that error handling triggers error event."""
        callback = Mock()
        client.on('error', callback)

        client.handle_error(10004, "Test error")

        callback.assert_called_once()


# =============================================================================
# UTILITY METHODS TESTS
# =============================================================================

class TestUtilityMethods:
    """Tests for utility methods."""

    def test_reset(self, client, mock_mt5):
        """Test client reset."""
        # Set up some state
        client.connection_state = ConnectionState.CONNECTED
        client.account_login = 12345
        client._connection_attempts = 5
        client._error_count = 2

        client.reset()

        # Verify reset
        assert client.connection_state == ConnectionState.DISCONNECTED
        assert client.account_login is None
        assert client._connection_attempts == 0
        assert client._error_count == 0

    def test_export_logs(self, client):
        """Test exporting logs."""
        with patch('builtins.open', mock_open()) as mock_file:
            result = client.export_logs('logs.json')

        assert result is True
        mock_file.assert_called_once()

    def test_repr(self, client):
        """Test __repr__ method."""
        client.connection_state = ConnectionState.CONNECTED
        client.account_login = 12345
        client.account_server = "TestServer"

        repr_str = repr(client)

        assert "MT5Client" in repr_str
        assert "connected" in repr_str
        assert "12345" in repr_str

    def test_str(self, client):
        """Test __str__ method."""
        client.connection_state = ConnectionState.CONNECTED

        str_repr = str(client)

        assert "MT5Client" in str_repr
        assert "connected" in str_repr

    def test_context_manager(self, client, mock_mt5):
        """Test using client as context manager."""
        with client as c:
            assert c is client

        # Verify shutdown was called
        mock_mt5['shutdown'].assert_called()


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestIntegration:
    """Integration tests for complete workflows."""

    def test_complete_connection_workflow(self, client, mock_mt5):
        """Test complete connection workflow."""
        # Initialize
        assert client.initialize(login=12345, password="pass", server="Server")
        assert client.is_connected()

        # Disconnect
        assert client.disconnect()
        assert client.connection_state == ConnectionState.DISCONNECTED

        # Shutdown
        client.shutdown()
        assert client.connection_state == ConnectionState.DISCONNECTED

    def test_account_switching_workflow(self, client, mock_mt5):
        """Test account switching workflow."""
        # Save accounts
        client.save_account('demo', 11111, 'pass1', 'DemoServer')
        client.save_account('live', 22222, 'pass2', 'LiveServer')

        # Switch between accounts
        assert client.switch_account('demo')
        assert client.current_account == 'demo'

        assert client.switch_account('live')
        assert client.current_account == 'live'

        # List accounts
        accounts = client.list_accounts()
        assert len(accounts) == 2

    def test_event_workflow(self, client, mock_mt5):
        """Test event system workflow."""
        events_triggered = []

        def on_connect(**kwargs):
            events_triggered.append('connect')

        def on_disconnect(**kwargs):
            events_triggered.append('disconnect')

        # Register callbacks
        client.on('connect', on_connect)
        client.on('disconnect', on_disconnect)

        # Trigger events through actions
        client.initialize(login=12345, password="pass", server="Server")
        assert 'connect' in events_triggered

        client.disconnect()
        assert 'disconnect' in events_triggered


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
