"""Tests for MT5Terminal class"""

from mylogger import logger
import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
from mymt5.terminal import MT5Terminal


@pytest.fixture
def mock_client():
    """Create a mock MT5Client instance"""
    client = Mock()
    client.is_connected.return_value = True
    return client


@pytest.fixture
def mock_terminal_info():
    """Create mock terminal info"""
    terminal_info = Mock()
    terminal_info.community_account = False
    terminal_info.community_connection = False
    terminal_info.connected = True
    terminal_info.dlls_allowed = True
    terminal_info.trade_allowed = True
    terminal_info.tradeapi_disabled = False
    terminal_info.email_enabled = True
    terminal_info.ftp_enabled = False
    terminal_info.notifications_enabled = True
    terminal_info.mqid = False
    terminal_info.build = 3730
    terminal_info.maxbars = 100000
    terminal_info.codepage = 1252
    terminal_info.ping_last = 45
    terminal_info.community_balance = 0.0
    terminal_info.retransmission = 0.0
    terminal_info.company = "MetaQuotes Ltd."
    terminal_info.name = "MetaTrader 5"
    terminal_info.language = "English"
    terminal_info.path = "C:\\Program Files\\MetaTrader 5"
    terminal_info.data_path = "C:\\Users\\User\\AppData\\Roaming\\MetaQuotes\\Terminal\\D0E8209F77C8CF37AD8BF550E51FF075"
    terminal_info.commondata_path = "C:\\Users\\User\\AppData\\Roaming\\MetaQuotes\\Terminal\\Common"
    return terminal_info


@pytest.fixture
def terminal(mock_client):
    """Create MT5Terminal instance"""
    return MT5Terminal(mock_client)


class TestMT5TerminalInit:
    """Test MT5Terminal initialization"""

    def test_init(self, mock_client):
        """Test terminal initialization"""
        terminal = MT5Terminal(mock_client)
        assert terminal.client == mock_client
        assert terminal._terminal_info_cache is None
        assert terminal._cache_timestamp is None
        assert terminal._cache_duration == 5


class TestTerminalInformation:
    """Test terminal information methods"""

    @patch('mymt5.terminal.mt5')
    def test_get_all_info(self, mock_mt5, terminal, mock_terminal_info):
        """Test getting all terminal information"""
        mock_mt5.terminal_info.return_value = mock_terminal_info

        result = terminal.get()

        assert isinstance(result, dict)
        assert result['name'] == 'MetaTrader 5'
        assert result['build'] == 3730
        assert result['connected'] is True

    @patch('mymt5.terminal.mt5')
    def test_get_specific_attribute(self, mock_mt5, terminal, mock_terminal_info):
        """Test getting specific terminal attribute"""
        mock_mt5.terminal_info.return_value = mock_terminal_info

        build = terminal.get('build')
        assert build == 3730

        name = terminal.get('name')
        assert name == 'MetaTrader 5'

    @patch('mymt5.terminal.mt5')
    def test_get_invalid_attribute(self, mock_mt5, terminal, mock_terminal_info):
        """Test getting invalid attribute raises ValueError"""
        mock_mt5.terminal_info.return_value = mock_terminal_info

        with pytest.raises(ValueError):
            terminal.get('invalid_attribute')

    @patch('mymt5.terminal.mt5')
    def test_get_failed(self, mock_mt5, terminal):
        """Test failed terminal info retrieval"""
        mock_mt5.terminal_info.return_value = None
        mock_mt5.last_error.return_value = (1, "Terminal not initialized")

        with pytest.raises(RuntimeError):
            terminal.get()

    @patch('mymt5.terminal.mt5')
    def test_info_caching(self, mock_mt5, terminal, mock_terminal_info):
        """Test terminal info caching"""
        mock_mt5.terminal_info.return_value = mock_terminal_info

        # First call
        result1 = terminal.get()
        # Second call should use cache
        result2 = terminal.get()

        assert result1 == result2
        # Should only call MT5 API once due to caching
        assert mock_mt5.terminal_info.call_count == 1


class TestTerminalStatus:
    """Test terminal status check methods"""

    @patch('mymt5.terminal.mt5')
    def test_check_connected(self, mock_mt5, terminal, mock_terminal_info):
        """Test checking if terminal is connected"""
        mock_mt5.terminal_info.return_value = mock_terminal_info
        mock_terminal_info.connected = True

        result = terminal.check('connected')

        assert result is True

    @patch('mymt5.terminal.mt5')
    def test_check_trade_allowed(self, mock_mt5, terminal, mock_terminal_info):
        """Test checking if trading is allowed"""
        mock_mt5.terminal_info.return_value = mock_terminal_info
        mock_terminal_info.trade_allowed = True

        result = terminal.check('trade_allowed')

        assert result is True

    @patch('mymt5.terminal.mt5')
    def test_check_dlls_allowed(self, mock_mt5, terminal, mock_terminal_info):
        """Test checking if DLLs are allowed"""
        mock_mt5.terminal_info.return_value = mock_terminal_info
        mock_terminal_info.dlls_allowed = True

        result = terminal.check('dlls_allowed')

        assert result is True

    @patch('mymt5.terminal.mt5')
    def test_check_email_enabled(self, mock_mt5, terminal, mock_terminal_info):
        """Test checking if email is enabled"""
        mock_mt5.terminal_info.return_value = mock_terminal_info
        mock_terminal_info.email_enabled = True

        result = terminal.check('email_enabled')

        assert result is True

    @patch('mymt5.terminal.mt5')
    def test_check_notifications_enabled(self, mock_mt5, terminal, mock_terminal_info):
        """Test checking if notifications are enabled"""
        mock_mt5.terminal_info.return_value = mock_terminal_info
        mock_terminal_info.notifications_enabled = True

        result = terminal.check('notifications_enabled')

        assert result is True

    @patch('mymt5.terminal.mt5')
    def test_check_tradeapi_disabled(self, mock_mt5, terminal, mock_terminal_info):
        """Test checking if trade API is disabled"""
        mock_mt5.terminal_info.return_value = mock_terminal_info
        mock_terminal_info.tradeapi_disabled = False

        result = terminal.check('tradeapi_disabled')

        assert result is False

    def test_check_invalid_status(self, terminal):
        """Test invalid status type raises ValueError"""
        with pytest.raises(ValueError):
            terminal.check('invalid_status')


class TestTerminalProperties:
    """Test terminal properties methods"""

    @patch('mymt5.terminal.mt5')
    def test_get_properties_resources(self, mock_mt5, terminal, mock_terminal_info):
        """Test getting terminal resources"""
        mock_mt5.terminal_info.return_value = mock_terminal_info

        result = terminal.get_properties('resources')

        assert isinstance(result, dict)
        assert 'maxbars' in result
        assert 'ping_last' in result
        assert result['maxbars'] == 100000
        assert result['ping_last'] == 45

    @patch('mymt5.terminal.mt5')
    def test_get_properties_display(self, mock_mt5, terminal, mock_terminal_info):
        """Test getting terminal display info"""
        mock_mt5.terminal_info.return_value = mock_terminal_info

        result = terminal.get_properties('display')

        assert isinstance(result, dict)
        assert 'name' in result
        assert 'company' in result
        assert 'language' in result
        assert result['name'] == 'MetaTrader 5'

    @patch('mymt5.terminal.mt5')
    def test_get_properties_limits(self, mock_mt5, terminal, mock_terminal_info):
        """Test getting terminal limits"""
        mock_mt5.terminal_info.return_value = mock_terminal_info

        result = terminal.get_properties('limits')

        assert isinstance(result, dict)
        assert 'dlls_allowed' in result
        assert 'trade_allowed' in result
        assert result['trade_allowed'] is True

    @patch('mymt5.terminal.mt5')
    def test_get_properties_all(self, mock_mt5, terminal, mock_terminal_info):
        """Test getting all terminal properties"""
        mock_mt5.terminal_info.return_value = mock_terminal_info

        result = terminal.get_properties('all')

        assert isinstance(result, dict)
        assert 'resources' in result
        assert 'display' in result
        assert 'limits' in result

    def test_get_properties_invalid_type(self, terminal):
        """Test invalid property type raises ValueError"""
        with pytest.raises(ValueError):
            terminal.get_properties('invalid_type')


class TestUtilityMethods:
    """Test utility methods"""

    @patch('mymt5.terminal.mt5')
    def test_get_summary(self, mock_mt5, terminal, mock_terminal_info):
        """Test getting terminal summary"""
        mock_mt5.terminal_info.return_value = mock_terminal_info

        result = terminal.get_summary()

        assert isinstance(result, dict)
        assert result['name'] == 'MetaTrader 5'
        assert result['build'] == 3730
        assert result['connected'] is True
        assert 'trade_allowed' in result
        assert 'path' in result

    @patch('mymt5.terminal.mt5')
    def test_print_info(self, mock_mt5, terminal, mock_terminal_info, capsys):
        """Test printing terminal info"""
        mock_mt5.terminal_info.return_value = mock_terminal_info

        terminal.print_info()

        captured = capsys.readouterr()
        assert 'MT5 TERMINAL INFORMATION' in captured.out
        assert 'MetaTrader 5' in captured.out
        assert '3730' in captured.out

    @patch('mymt5.terminal.mt5')
    def test_export_dict(self, mock_mt5, terminal, mock_terminal_info):
        """Test exporting terminal info as dict"""
        mock_mt5.terminal_info.return_value = mock_terminal_info

        result = terminal.export('dict')

        assert isinstance(result, dict)
        assert result['name'] == 'MetaTrader 5'

    @patch('mymt5.terminal.mt5')
    def test_export_json(self, mock_mt5, terminal, mock_terminal_info):
        """Test exporting terminal info as JSON"""
        mock_mt5.terminal_info.return_value = mock_terminal_info

        result = terminal.export('json')

        assert isinstance(result, str)
        assert 'MetaTrader 5' in result

    @patch('mymt5.terminal.mt5')
    def test_export_json_to_file(self, mock_mt5, terminal, mock_terminal_info, tmp_path):
        """Test exporting terminal info to JSON file"""
        mock_mt5.terminal_info.return_value = mock_terminal_info
        filepath = str(tmp_path / "terminal.json")

        result = terminal.export('json', filepath)

        assert "Exported to" in result
        assert filepath in result

    @patch('mymt5.terminal.mt5')
    def test_export_csv_to_file(self, mock_mt5, terminal, mock_terminal_info, tmp_path):
        """Test exporting terminal info to CSV file"""
        mock_mt5.terminal_info.return_value = mock_terminal_info
        filepath = str(tmp_path / "terminal.csv")

        result = terminal.export('csv', filepath)

        assert "Exported to" in result
        assert filepath in result

    @patch('mymt5.terminal.mt5')
    def test_export_invalid_format(self, mock_mt5, terminal, mock_terminal_info):
        """Test invalid export format raises ValueError"""
        mock_mt5.terminal_info.return_value = mock_terminal_info

        with pytest.raises(ValueError):
            terminal.export('invalid_format')


class TestCompatibility:
    """Test compatibility check methods"""

    @patch('mymt5.terminal.mt5')
    @patch('mymt5.terminal.sys')
    @patch('mymt5.terminal.platform')
    def test_check_compatibility(self, mock_platform, mock_sys, mock_mt5, terminal, mock_terminal_info):
        """Test checking system compatibility"""
        mock_mt5.terminal_info.return_value = mock_terminal_info
        mock_mt5.version.return_value = (5, 0, 37)

        # Mock Python version
        mock_sys.version = "3.10.0"
        mock_sys.version_info = Mock(major=3, minor=10, micro=0)

        # Mock platform info
        mock_platform.system.return_value = "Windows"
        mock_platform.release.return_value = "10"
        mock_platform.version.return_value = "10.0.19041"
        mock_platform.machine.return_value = "AMD64"
        mock_platform.processor.return_value = "Intel64 Family 6 Model 142 Stepping 12, GenuineIntel"

        result = terminal.check_compatibility()

        assert isinstance(result, dict)
        assert 'python' in result
        assert 'system' in result
        assert 'mt5' in result
        assert 'terminal' in result
        assert 'overall_status' in result
        assert result['python']['compatible'] is True

    @patch('mymt5.terminal.mt5')
    @patch('mymt5.terminal.sys')
    @patch('mymt5.terminal.platform')
    def test_check_compatibility_python_incompatible(self, mock_platform, mock_sys, mock_mt5, terminal, mock_terminal_info):
        """Test compatibility check with incompatible Python version"""
        mock_mt5.terminal_info.return_value = mock_terminal_info
        mock_mt5.version.return_value = (5, 0, 37)

        # Mock old Python version
        mock_sys.version = "3.6.0"
        mock_sys.version_info = Mock(major=3, minor=6, micro=0)

        mock_platform.system.return_value = "Windows"
        mock_platform.release.return_value = "10"
        mock_platform.version.return_value = "10.0.19041"
        mock_platform.machine.return_value = "AMD64"
        mock_platform.processor.return_value = "Intel64 Family 6 Model 142 Stepping 12, GenuineIntel"

        result = terminal.check_compatibility()

        assert result['python']['compatible'] is False
        assert 'Warning' in result['overall_status'] or 'issue' in result['overall_status']

    @patch('mymt5.terminal.mt5')
    @patch('mymt5.terminal.sys')
    @patch('mymt5.terminal.platform')
    def test_check_compatibility_not_connected(self, mock_platform, mock_sys, mock_mt5, terminal, mock_terminal_info):
        """Test compatibility check when terminal not connected"""
        mock_terminal_info.connected = False
        mock_mt5.terminal_info.return_value = mock_terminal_info
        mock_mt5.version.return_value = (5, 0, 37)

        mock_sys.version = "3.10.0"
        mock_sys.version_info = Mock(major=3, minor=10, micro=0)

        mock_platform.system.return_value = "Windows"
        mock_platform.release.return_value = "10"
        mock_platform.version.return_value = "10.0.19041"
        mock_platform.machine.return_value = "AMD64"
        mock_platform.processor.return_value = "Intel64 Family 6 Model 142 Stepping 12, GenuineIntel"

        result = terminal.check_compatibility()

        assert 'not connected' in result['overall_status'].lower()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
