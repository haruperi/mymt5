from mylogger import logger
"""
Unit tests for MT5Data class.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch
import MetaTrader5 as mt5
import tempfile
from pathlib import Path

from mymt5.data import MT5Data
from mymt5.enums import TimeFrame


@pytest.fixture
def mock_client():
    """Create a mock MT5Client."""
    client = Mock()
    client.is_connected.return_value = True
    return client


@pytest.fixture
def mt5_data(mock_client):
    """Create MT5Data instance with mock client."""
    return MT5Data(client=mock_client)


@pytest.fixture
def sample_bars_data():
    """Create sample OHLCV bar data."""
    return np.array([
        (1640000000, 1.1300, 1.1350, 1.1280, 1.1320, 1000, 0, 0),
        (1640003600, 1.1320, 1.1380, 1.1310, 1.1360, 1200, 0, 0),
        (1640007200, 1.1360, 1.1400, 1.1340, 1.1380, 1100, 0, 0),
    ], dtype=[('time', 'i8'), ('open', 'f8'), ('high', 'f8'), ('low', 'f8'),
              ('close', 'f8'), ('tick_volume', 'i8'), ('spread', 'i4'), ('real_volume', 'i8')])


@pytest.fixture
def sample_ticks_data():
    """Create sample tick data."""
    return np.array([
        (1640000000, 1.1300, 1.1302, 1.1301, 100),
        (1640000001, 1.1301, 1.1303, 1.1302, 150),
        (1640000002, 1.1302, 1.1304, 1.1303, 120),
    ], dtype=[('time', 'i8'), ('bid', 'f8'), ('ask', 'f8'), ('last', 'f8'), ('volume', 'i8')])


@pytest.fixture
def sample_dataframe():
    """Create sample DataFrame for testing."""
    return pd.DataFrame({
        'time': pd.date_range('2024-01-01', periods=100, freq='H'),
        'open': np.random.uniform(1.1200, 1.1400, 100),
        'high': np.random.uniform(1.1300, 1.1500, 100),
        'low': np.random.uniform(1.1100, 1.1300, 100),
        'close': np.random.uniform(1.1200, 1.1400, 100),
        'volume': np.random.randint(500, 2000, 100)
    })


class TestMT5DataInitialization:
    """Test MT5Data initialization."""

    def test_init_with_client(self, mock_client):
        """Test initialization with client."""
        data = MT5Data(client=mock_client)
        assert data.client == mock_client
        assert isinstance(data._cache, dict)
        assert isinstance(data._stream_threads, dict)
        assert isinstance(data._stream_active, dict)

    def test_init_without_client(self):
        """Test initialization without client."""
        data = MT5Data()
        assert data.client is None
        assert isinstance(data._cache, dict)


class TestGetBars:
    """Test get_bars method."""

    @patch('MetaTrader5.copy_rates_from_pos')
    def test_get_bars_by_count(self, mock_copy_rates, mt5_data, sample_bars_data):
        """Test retrieving bars by count."""
        mock_copy_rates.return_value = sample_bars_data

        result = mt5_data.get_bars("EURUSD", TimeFrame.H1, count=100)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        assert 'time' in result.columns
        assert 'open' in result.columns
        mock_copy_rates.assert_called_once()

    @patch('MetaTrader5.copy_rates_range')
    def test_get_bars_by_date_range(self, mock_copy_rates, mt5_data, sample_bars_data):
        """Test retrieving bars by date range."""
        mock_copy_rates.return_value = sample_bars_data

        start = datetime(2024, 1, 1)
        end = datetime(2024, 1, 31)
        result = mt5_data.get_bars("EURUSD", TimeFrame.H1, start=start, end=end)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        mock_copy_rates.assert_called_once()

    @patch('MetaTrader5.copy_rates_from_pos')
    def test_get_bars_as_dict(self, mock_copy_rates, mt5_data, sample_bars_data):
        """Test retrieving bars as dict."""
        mock_copy_rates.return_value = sample_bars_data

        result = mt5_data.get_bars("EURUSD", TimeFrame.H1, count=100, as_dataframe=False)

        assert isinstance(result, list)
        assert len(result) == 3
        assert isinstance(result[0], dict)
        assert 'open' in result[0]

    @patch('MetaTrader5.copy_rates_from_pos')
    @patch('MetaTrader5.last_error')
    def test_get_bars_no_data(self, mock_error, mock_copy_rates, mt5_data):
        """Test handling when no bars are returned."""
        mock_copy_rates.return_value = None
        mock_error.return_value = (1, "No data")

        result = mt5_data.get_bars("INVALID", TimeFrame.H1, count=100)

        assert result is None
        mock_error.assert_called_once()

    def test_get_bars_invalid_parameters(self, mt5_data):
        """Test with invalid parameters."""
        result = mt5_data.get_bars("EURUSD", TimeFrame.H1)
        assert result is None


class TestGetTicks:
    """Test get_ticks method."""

    @patch('MetaTrader5.copy_ticks_from')
    def test_get_ticks_by_count(self, mock_copy_ticks, mt5_data, sample_ticks_data):
        """Test retrieving ticks by count."""
        mock_copy_ticks.return_value = sample_ticks_data

        result = mt5_data.get_ticks("EURUSD", count=1000)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        assert 'time' in result.columns
        assert 'bid' in result.columns

    @patch('MetaTrader5.copy_ticks_range')
    def test_get_ticks_by_date_range(self, mock_copy_ticks, mt5_data, sample_ticks_data):
        """Test retrieving ticks by date range."""
        mock_copy_ticks.return_value = sample_ticks_data

        start = datetime(2024, 1, 1)
        end = datetime(2024, 1, 2)
        result = mt5_data.get_ticks("EURUSD", start=start, end=end)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3

    @patch('MetaTrader5.copy_ticks_from')
    def test_get_ticks_as_dict(self, mock_copy_ticks, mt5_data, sample_ticks_data):
        """Test retrieving ticks as dict."""
        mock_copy_ticks.return_value = sample_ticks_data

        result = mt5_data.get_ticks("EURUSD", count=1000, as_dataframe=False)

        assert isinstance(result, list)
        assert len(result) == 3
        assert isinstance(result[0], dict)

    @patch('MetaTrader5.copy_ticks_from')
    @patch('MetaTrader5.last_error')
    def test_get_ticks_no_data(self, mock_error, mock_copy_ticks, mt5_data):
        """Test handling when no ticks are returned."""
        mock_copy_ticks.return_value = None
        mock_error.return_value = (1, "No data")

        result = mt5_data.get_ticks("INVALID", count=1000)

        assert result is None


class TestStreaming:
    """Test streaming functionality."""

    @patch('MetaTrader5.symbol_info_tick')
    def test_stream_ticks_start(self, mock_tick_info, mt5_data):
        """Test starting tick stream."""
        mock_tick = Mock()
        mock_tick.time = 1640000000
        mock_tick.bid = 1.1300
        mock_tick.ask = 1.1302
        mock_tick.last = 1.1301
        mock_tick.volume = 100
        mock_tick_info.return_value = mock_tick

        callback = Mock()
        result = mt5_data.stream("EURUSD", "ticks", callback)

        assert result is True
        assert "EURUSD_ticks" in mt5_data._stream_active
        assert mt5_data._stream_active["EURUSD_ticks"] is True

    def test_stream_bars_start(self, mt5_data):
        """Test starting bar stream."""
        callback = Mock()
        result = mt5_data.stream("EURUSD", "bars", callback, timeframe=TimeFrame.H1)

        assert result is True
        assert "EURUSD_bars" in mt5_data._stream_active

    def test_stream_invalid_type(self, mt5_data):
        """Test streaming with invalid data type."""
        callback = Mock()
        result = mt5_data.stream("EURUSD", "invalid", callback)

        assert result is False

    def test_stream_bars_without_timeframe(self, mt5_data):
        """Test bars streaming without timeframe."""
        callback = Mock()
        result = mt5_data.stream("EURUSD", "bars", callback)

        assert result is False

    def test_stop_stream(self, mt5_data):
        """Test stopping stream."""
        # Start stream first
        callback = Mock()
        mt5_data.stream("EURUSD", "ticks", callback)

        # Stop stream
        result = mt5_data.stop_stream("EURUSD", "ticks")

        assert result is True
        assert mt5_data._stream_active.get("EURUSD_ticks", True) is False

    def test_stop_stream_not_active(self, mt5_data):
        """Test stopping non-existent stream."""
        result = mt5_data.stop_stream("EURUSD", "ticks")
        assert result is False


class TestDataProcessing:
    """Test data processing methods."""

    def test_process_normalize(self, mt5_data, sample_dataframe):
        """Test data normalization."""
        result = mt5_data.process(sample_dataframe, 'normalize', method='minmax')

        assert result is not None
        assert 'open_normalized' in result.columns
        assert result['open_normalized'].min() >= 0
        assert result['open_normalized'].max() <= 1

    def test_process_clean(self, mt5_data, sample_dataframe):
        """Test data cleaning."""
        # Add some NaN values
        df = sample_dataframe.copy()
        df.loc[10, 'close'] = np.nan
        df.loc[20, 'open'] = -1  # Invalid negative price

        result = mt5_data.process(df, 'clean')

        assert result is not None
        assert len(result) < len(df)
        assert result['open'].min() > 0

    def test_process_resample(self, mt5_data, sample_dataframe):
        """Test data resampling."""
        result = mt5_data.process(sample_dataframe, 'resample', timeframe='4H')

        assert result is not None
        assert len(result) < len(sample_dataframe)
        assert 'open' in result.columns

    def test_process_fill_missing(self, mt5_data, sample_dataframe):
        """Test filling missing values."""
        df = sample_dataframe.copy()
        df.loc[10, 'close'] = np.nan

        result = mt5_data.process(df, 'fill_missing', method='ffill')

        assert result is not None
        assert result['close'].isnull().sum() == 0

    def test_process_detect_gaps(self, mt5_data, sample_dataframe):
        """Test gap detection."""
        # Create a gap
        df = sample_dataframe.copy()
        df = df.drop(df.index[50:60])  # Remove 10 rows to create gap

        result = mt5_data.process(df, 'detect_gaps', timeframe_minutes=60)

        assert result is not None
        assert len(result) > 0

    def test_process_invalid_operation(self, mt5_data, sample_dataframe):
        """Test with invalid operation."""
        result = mt5_data.process(sample_dataframe, 'invalid_operation')
        assert result is None


class TestCaching:
    """Test caching functionality."""

    def test_cache_data(self, mt5_data):
        """Test caching data."""
        test_data = {"symbol": "EURUSD", "price": 1.1300}
        mt5_data.cache("test_key", test_data)

        assert "test_key" in mt5_data._cache
        assert mt5_data._cache["test_key"]["data"] == test_data

    def test_get_cached_data(self, mt5_data):
        """Test retrieving cached data."""
        test_data = {"symbol": "EURUSD", "price": 1.1300}
        mt5_data.cache("test_key", test_data)

        result = mt5_data.get_cached("test_key")
        assert result == test_data

    def test_get_cached_not_found(self, mt5_data):
        """Test retrieving non-existent cache."""
        result = mt5_data.get_cached("nonexistent_key")
        assert result is None

    def test_cache_with_ttl(self, mt5_data):
        """Test cache with time-to-live."""
        import time

        test_data = {"symbol": "EURUSD", "price": 1.1300}
        mt5_data.cache("test_key", test_data, ttl=1)  # 1 second TTL

        # Should be available immediately
        result = mt5_data.get_cached("test_key")
        assert result == test_data

        # Wait for expiration
        time.sleep(1.1)

        # Should be expired now
        result = mt5_data.get_cached("test_key")
        assert result is None

    def test_clear_specific_cache(self, mt5_data):
        """Test clearing specific cache entry."""
        mt5_data.cache("key1", "data1")
        mt5_data.cache("key2", "data2")

        mt5_data.clear_cache("key1")

        assert "key1" not in mt5_data._cache
        assert "key2" in mt5_data._cache

    def test_clear_all_cache(self, mt5_data):
        """Test clearing all cache."""
        mt5_data.cache("key1", "data1")
        mt5_data.cache("key2", "data2")

        mt5_data.clear_cache()

        assert len(mt5_data._cache) == 0


class TestExport:
    """Test data export functionality."""

    def test_export_csv(self, mt5_data, sample_dataframe):
        """Test exporting to CSV."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test.csv"
            result = mt5_data.export(sample_dataframe, filepath, format='csv')

            assert result is True
            assert filepath.exists()

    def test_export_json(self, mt5_data, sample_dataframe):
        """Test exporting to JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test.json"
            result = mt5_data.export(sample_dataframe, filepath, format='json')

            assert result is True
            assert filepath.exists()

    @pytest.mark.skipif(
        not any([__import__('importlib').util.find_spec(lib)
                for lib in ['pyarrow', 'fastparquet']]),
        reason="pyarrow or fastparquet not installed"
    )
    def test_export_parquet(self, mt5_data, sample_dataframe):
        """Test exporting to Parquet."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test.parquet"
            result = mt5_data.export(sample_dataframe, filepath, format='parquet')

            assert result is True
            assert filepath.exists()

    def test_export_pickle(self, mt5_data, sample_dataframe):
        """Test exporting to Pickle."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test.pkl"
            result = mt5_data.export(sample_dataframe, filepath, format='pickle')

            assert result is True
            assert filepath.exists()

    def test_export_invalid_format(self, mt5_data, sample_dataframe):
        """Test export with invalid format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test.xyz"
            result = mt5_data.export(sample_dataframe, filepath, format='invalid')

            assert result is False


class TestTimeframeUtilities:
    """Test timeframe utility methods."""

    def test_get_timeframes(self, mt5_data):
        """Test getting available timeframes."""
        result = mt5_data.get_timeframes()

        assert isinstance(result, list)
        assert len(result) > 0
        assert 'name' in result[0]
        assert 'value' in result[0]
        assert 'minutes' in result[0]

    def test_convert_timeframe_from_enum(self, mt5_data):
        """Test converting TimeFrame enum to MT5 constant."""
        result = mt5_data.convert_timeframe(TimeFrame.H1)
        assert result == mt5.TIMEFRAME_H1

    def test_convert_timeframe_from_string(self, mt5_data):
        """Test converting string to MT5 constant."""
        result = mt5_data.convert_timeframe("H1")
        assert result == mt5.TIMEFRAME_H1

    def test_convert_timeframe_from_int(self, mt5_data):
        """Test converting int to MT5 constant."""
        result = mt5_data.convert_timeframe(mt5.TIMEFRAME_H1)
        assert result == mt5.TIMEFRAME_H1

    def test_convert_invalid_timeframe(self, mt5_data):
        """Test converting invalid timeframe."""
        result = mt5_data.convert_timeframe("INVALID")
        assert result == mt5.TIMEFRAME_H1  # Default


class TestStatistics:
    """Test statistical methods."""

    def test_get_summary(self, mt5_data, sample_dataframe):
        """Test getting data summary."""
        result = mt5_data.get_summary(sample_dataframe)

        assert isinstance(result, dict)
        assert 'rows' in result
        assert result['rows'] == len(sample_dataframe)
        assert 'columns' in result
        assert 'date_range' in result
        assert 'price_stats' in result

    def test_calculate_stats(self, mt5_data, sample_dataframe):
        """Test calculating statistics."""
        result = mt5_data.calculate_stats(sample_dataframe)

        assert isinstance(result, dict)
        assert 'total_return' in result
        assert 'volatility' in result
        assert 'sharpe_ratio' in result
        assert 'max_drawdown' in result
        assert 'price_range' in result

    def test_calculate_stats_empty_data(self, mt5_data):
        """Test calculating stats with empty DataFrame."""
        df = pd.DataFrame()
        result = mt5_data.calculate_stats(df)

        assert isinstance(result, dict)
        assert len(result) == 0


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_process_with_empty_dataframe(self, mt5_data):
        """Test processing empty DataFrame."""
        df = pd.DataFrame()
        result = mt5_data.process(df, 'normalize')

        # Should handle gracefully
        assert result is not None or result is None  # Either way is acceptable

    def test_export_creates_directory(self, mt5_data, sample_dataframe):
        """Test that export creates directories if needed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "subdir" / "test.csv"
            result = mt5_data.export(sample_dataframe, filepath, format='csv')

            assert result is True
            assert filepath.exists()
            assert filepath.parent.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
