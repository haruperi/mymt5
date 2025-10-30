from mylogger import logger
"""
Unit tests for MT5History class.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch
import MetaTrader5 as mt5
import tempfile
from pathlib import Path
from collections import namedtuple

from mymt5.history import MT5History


@pytest.fixture
def mock_client():
    """Create a mock MT5Client."""
    client = Mock()
    client.is_connected.return_value = True
    return client


@pytest.fixture
def mt5_history(mock_client):
    """Create MT5History instance with mock client."""
    return MT5History(client=mock_client)


@pytest.fixture
def sample_deals():
    """Create sample deals data."""
    # Create named tuple to simulate MT5 deal structure
    Deal = namedtuple('Deal', ['ticket', 'order', 'time', 'type', 'entry', 'magic',
                               'position_id', 'reason', 'volume', 'price', 'commission',
                               'swap', 'profit', 'fee', 'symbol', 'comment', 'external_id'])

    deals = [
        Deal(1, 1, 1640000000, 0, 0, 0, 1, 0, 0.1, 1.1300, -0.5, 0.0, 100.0, 0.0, 'EURUSD', '', ''),
        Deal(2, 2, 1640003600, 1, 1, 0, 1, 0, 0.1, 1.1350, -0.5, 0.0, 50.0, 0.0, 'EURUSD', '', ''),
        Deal(3, 3, 1640007200, 0, 0, 0, 2, 0, 0.1, 1.1280, -0.5, 0.0, -30.0, 0.0, 'EURUSD', '', ''),
        Deal(4, 4, 1640010800, 0, 0, 0, 3, 0, 0.2, 1.1800, -1.0, 0.0, 200.0, 0.0, 'GBPUSD', '', ''),
        Deal(5, 5, 1640014400, 1, 1, 0, 3, 0, 0.2, 1.1850, -1.0, 0.0, -50.0, 0.0, 'GBPUSD', '', ''),
    ]

    return tuple(deals)


@pytest.fixture
def sample_orders():
    """Create sample orders data."""
    Order = namedtuple('Order', ['ticket', 'time_setup', 'time_done', 'type', 'type_time',
                                 'type_filling', 'state', 'magic', 'position_id',
                                 'volume_initial', 'volume_current', 'price_open',
                                 'price_current', 'symbol', 'comment', 'external_id'])

    orders = [
        Order(1, 1640000000, 1640003600, 0, 0, 0, 1, 0, 1, 0.1, 0.0, 1.1300, 1.1350, 'EURUSD', '', ''),
        Order(2, 1640007200, 1640010800, 0, 0, 0, 1, 0, 2, 0.1, 0.0, 1.1280, 1.1250, 'EURUSD', '', ''),
        Order(3, 1640014400, 1640018000, 0, 0, 0, 1, 0, 3, 0.2, 0.0, 1.1800, 1.1850, 'GBPUSD', '', ''),
    ]

    return tuple(orders)


@pytest.fixture
def sample_deals_df(sample_deals):
    """Create sample deals DataFrame."""
    df = pd.DataFrame([deal._asdict() for deal in sample_deals])
    df['time'] = pd.to_datetime(df['time'], unit='s')
    return df


class TestMT5HistoryInitialization:
    """Test MT5History initialization."""

    def test_init_with_client(self, mock_client):
        """Test initialization with client."""
        history = MT5History(client=mock_client)
        assert history.client == mock_client
        assert isinstance(history._cache, dict)

    def test_init_without_client(self):
        """Test initialization without client."""
        history = MT5History()
        assert history.client is None
        assert isinstance(history._cache, dict)


class TestHistoryRetrieval:
    """Test history retrieval methods."""

    @patch('MetaTrader5.history_deals_get')
    def test_get_deals(self, mock_deals_get, mt5_history, sample_deals):
        """Test retrieving deals."""
        mock_deals_get.return_value = sample_deals

        result = mt5_history.get('deals', start=datetime(2021, 12, 1), end=datetime(2021, 12, 31))

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 5
        assert 'profit' in result.columns
        assert 'symbol' in result.columns
        mock_deals_get.assert_called_once()

    @patch('MetaTrader5.history_orders_get')
    def test_get_orders(self, mock_orders_get, mt5_history, sample_orders):
        """Test retrieving orders."""
        mock_orders_get.return_value = sample_orders

        result = mt5_history.get('orders', start=datetime(2021, 12, 1), end=datetime(2021, 12, 31))

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        assert 'symbol' in result.columns
        mock_orders_get.assert_called_once()

    @patch('MetaTrader5.history_deals_get')
    @patch('MetaTrader5.history_orders_get')
    def test_get_both(self, mock_orders_get, mock_deals_get, mt5_history, sample_deals, sample_orders):
        """Test retrieving both deals and orders."""
        mock_deals_get.return_value = sample_deals
        mock_orders_get.return_value = sample_orders

        result = mt5_history.get('both', start=datetime(2021, 12, 1), end=datetime(2021, 12, 31))

        assert isinstance(result, dict)
        assert 'deals' in result
        assert 'orders' in result
        assert len(result['deals']) == 5
        assert len(result['orders']) == 3

    @patch('MetaTrader5.history_deals_get')
    def test_get_deals_by_symbol(self, mock_deals_get, mt5_history, sample_deals):
        """Test filtering deals by symbol."""
        mock_deals_get.return_value = sample_deals

        result = mt5_history.get('deals', symbol='EURUSD', start=datetime(2021, 12, 1))

        assert len(result) == 3  # Only EURUSD deals
        assert all(result['symbol'] == 'EURUSD')

    @patch('MetaTrader5.history_deals_get')
    def test_get_no_deals(self, mock_deals_get, mt5_history):
        """Test handling when no deals are found."""
        mock_deals_get.return_value = ()

        result = mt5_history.get('deals', start=datetime(2021, 12, 1))

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0

    def test_get_invalid_type(self, mt5_history):
        """Test with invalid data type."""
        result = mt5_history.get('invalid')
        assert result is None


class TestQuickAccess:
    """Test quick access methods."""

    @patch('MetaTrader5.history_deals_get')
    def test_get_today(self, mock_deals_get, mt5_history, sample_deals):
        """Test getting today's deals."""
        mock_deals_get.return_value = sample_deals

        result = mt5_history.get_today('deals')

        assert isinstance(result, pd.DataFrame)
        mock_deals_get.assert_called_once()

    @patch('MetaTrader5.history_deals_get')
    def test_get_period_week(self, mock_deals_get, mt5_history, sample_deals):
        """Test getting week's deals."""
        mock_deals_get.return_value = sample_deals

        result = mt5_history.get_period('week', 'deals')

        assert isinstance(result, pd.DataFrame)
        mock_deals_get.assert_called_once()

    @patch('MetaTrader5.history_deals_get')
    def test_get_period_month(self, mock_deals_get, mt5_history, sample_deals):
        """Test getting month's deals."""
        mock_deals_get.return_value = sample_deals

        result = mt5_history.get_period('month', 'deals')

        assert isinstance(result, pd.DataFrame)

    @patch('MetaTrader5.history_deals_get')
    def test_get_period_year(self, mock_deals_get, mt5_history, sample_deals):
        """Test getting year's deals."""
        mock_deals_get.return_value = sample_deals

        result = mt5_history.get_period('year', 'deals')

        assert isinstance(result, pd.DataFrame)

    def test_get_period_invalid(self, mt5_history):
        """Test with invalid period."""
        result = mt5_history.get_period('invalid')
        assert result is None


class TestPerformanceMetrics:
    """Test performance metrics calculations."""

    def test_calculate_win_rate(self, mt5_history, sample_deals_df):
        """Test win rate calculation."""
        result = mt5_history.calculate('win_rate', deals=sample_deals_df)

        assert isinstance(result, float)
        assert 0 <= result <= 100
        # 3 winning trades out of 5
        assert result == 60.0

    def test_calculate_profit_factor(self, mt5_history, sample_deals_df):
        """Test profit factor calculation."""
        result = mt5_history.calculate('profit_factor', deals=sample_deals_df)

        assert isinstance(result, float)
        assert result > 0
        # (100 + 50 + 200) / (30 + 50) = 350 / 80 = 4.375
        assert result == pytest.approx(4.375, rel=0.01)

    def test_calculate_avg_win(self, mt5_history, sample_deals_df):
        """Test average win calculation."""
        result = mt5_history.calculate('avg_win', deals=sample_deals_df)

        assert isinstance(result, float)
        # (100 + 50 + 200) / 3 = 116.67
        assert result == pytest.approx(116.67, rel=0.01)

    def test_calculate_avg_loss(self, mt5_history, sample_deals_df):
        """Test average loss calculation."""
        result = mt5_history.calculate('avg_loss', deals=sample_deals_df)

        assert isinstance(result, float)
        assert result < 0
        # (-30 + -50) / 2 = -40
        assert result == pytest.approx(-40.0, rel=0.01)

    def test_calculate_largest_win(self, mt5_history, sample_deals_df):
        """Test largest win calculation."""
        result = mt5_history.calculate('largest_win', deals=sample_deals_df)

        assert result == 200.0

    def test_calculate_largest_loss(self, mt5_history, sample_deals_df):
        """Test largest loss calculation."""
        result = mt5_history.calculate('largest_loss', deals=sample_deals_df)

        assert result == -50.0

    def test_calculate_sharpe_ratio(self, mt5_history, sample_deals_df):
        """Test Sharpe ratio calculation."""
        result = mt5_history.calculate('sharpe_ratio', deals=sample_deals_df)

        assert isinstance(result, float)

    def test_calculate_max_drawdown(self, mt5_history, sample_deals_df):
        """Test max drawdown calculation."""
        result = mt5_history.calculate('max_drawdown', deals=sample_deals_df)

        assert isinstance(result, float)
        assert result <= 0

    def test_calculate_total_trades(self, mt5_history, sample_deals_df):
        """Test total trades count."""
        result = mt5_history.calculate('total_trades', deals=sample_deals_df)

        assert result == 5

    def test_calculate_total_profit(self, mt5_history, sample_deals_df):
        """Test total profit calculation."""
        result = mt5_history.calculate('total_profit', deals=sample_deals_df)

        assert result == 270.0  # 100 + 50 - 30 + 200 - 50

    def test_calculate_all_metrics(self, mt5_history, sample_deals_df):
        """Test calculating all metrics at once."""
        result = mt5_history.calculate('all', deals=sample_deals_df)

        assert isinstance(result, dict)
        assert 'win_rate' in result
        assert 'profit_factor' in result
        assert 'total_trades' in result
        assert 'total_profit' in result
        assert 'sharpe_ratio' in result
        assert 'max_drawdown' in result

    def test_calculate_invalid_metric(self, mt5_history, sample_deals_df):
        """Test with invalid metric."""
        result = mt5_history.calculate('invalid_metric', deals=sample_deals_df)
        assert result is None

    def test_calculate_empty_deals(self, mt5_history):
        """Test calculations with empty DataFrame."""
        empty_df = pd.DataFrame()
        result = mt5_history.calculate('win_rate', deals=empty_df)
        assert result is None


class TestTradeAnalysis:
    """Test trade analysis methods."""

    def test_analyze_by_symbol(self, mt5_history, sample_deals_df):
        """Test analysis by symbol."""
        result = mt5_history.analyze('by_symbol', deals=sample_deals_df)

        assert isinstance(result, pd.DataFrame)
        assert 'symbol' in result.columns
        assert 'trades' in result.columns
        assert 'total_profit' in result.columns
        assert 'win_rate' in result.columns
        assert len(result) == 2  # EURUSD and GBPUSD

    def test_analyze_by_hour(self, mt5_history, sample_deals_df):
        """Test analysis by hour."""
        result = mt5_history.analyze('by_hour', deals=sample_deals_df)

        assert isinstance(result, pd.DataFrame)
        assert 'time_unit' in result.columns
        assert 'trades' in result.columns

    def test_analyze_by_weekday(self, mt5_history, sample_deals_df):
        """Test analysis by weekday."""
        result = mt5_history.analyze('by_weekday', deals=sample_deals_df)

        assert isinstance(result, pd.DataFrame)
        assert 'time_unit' in result.columns

    def test_analyze_winning_trades(self, mt5_history, sample_deals_df):
        """Test filtering winning trades."""
        result = mt5_history.analyze('winning_trades', deals=sample_deals_df)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        assert all(result['profit'] > 0)

    def test_analyze_losing_trades(self, mt5_history, sample_deals_df):
        """Test filtering losing trades."""
        result = mt5_history.analyze('losing_trades', deals=sample_deals_df)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert all(result['profit'] < 0)

    def test_analyze_statistics(self, mt5_history, sample_deals_df):
        """Test statistical analysis."""
        result = mt5_history.analyze('statistics', deals=sample_deals_df)

        assert isinstance(result, dict)
        assert 'win_rate' in result

    def test_analyze_invalid_type(self, mt5_history, sample_deals_df):
        """Test with invalid analysis type."""
        result = mt5_history.analyze('invalid', deals=sample_deals_df)
        assert result is None


class TestReportGeneration:
    """Test report generation."""

    @patch('MetaTrader5.history_deals_get')
    def test_generate_performance_report(self, mock_deals_get, mt5_history, sample_deals):
        """Test performance report generation."""
        mock_deals_get.return_value = sample_deals

        result = mt5_history.generate_report('performance', format='dict')

        assert isinstance(result, dict)
        assert 'win_rate' in result
        assert 'profit_factor' in result

    @patch('MetaTrader5.history_deals_get')
    def test_generate_summary_report(self, mock_deals_get, mt5_history, sample_deals):
        """Test summary report generation."""
        mock_deals_get.return_value = sample_deals

        result = mt5_history.generate_report('summary', format='dict')

        assert isinstance(result, dict)

    @patch('MetaTrader5.history_deals_get')
    def test_generate_detailed_report(self, mock_deals_get, mt5_history, sample_deals):
        """Test detailed report generation."""
        mock_deals_get.return_value = sample_deals

        result = mt5_history.generate_report('detailed', format='dict')

        assert isinstance(result, dict)
        assert 'metrics' in result
        assert 'by_symbol' in result

    @patch('MetaTrader5.history_deals_get')
    def test_generate_report_text_format(self, mock_deals_get, mt5_history, sample_deals):
        """Test report in text format."""
        mock_deals_get.return_value = sample_deals

        result = mt5_history.generate_report('summary', format='text')

        assert isinstance(result, str)
        assert 'SUMMARY REPORT' in result

    @patch('MetaTrader5.history_deals_get')
    def test_generate_report_html_format(self, mock_deals_get, mt5_history, sample_deals):
        """Test report in HTML format."""
        mock_deals_get.return_value = sample_deals

        result = mt5_history.generate_report('summary', format='html')

        assert isinstance(result, str)
        assert '<table' in result.lower()

    def test_generate_report_invalid_type(self, mt5_history):
        """Test with invalid report type."""
        result = mt5_history.generate_report('invalid')
        assert result is None


class TestExport:
    """Test export functionality."""

    @patch('MetaTrader5.history_deals_get')
    def test_export_csv(self, mock_deals_get, mt5_history, sample_deals):
        """Test exporting to CSV."""
        mock_deals_get.return_value = sample_deals

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "history.csv"
            result = mt5_history.export(filepath, 'deals', format='csv')

            assert result is True
            assert filepath.exists()

    @patch('MetaTrader5.history_deals_get')
    def test_export_json(self, mock_deals_get, mt5_history, sample_deals):
        """Test exporting to JSON."""
        mock_deals_get.return_value = sample_deals

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "history.json"
            result = mt5_history.export(filepath, 'deals', format='json')

            assert result is True
            assert filepath.exists()

    @pytest.mark.skipif(
        not __import__('importlib').util.find_spec('openpyxl'),
        reason="openpyxl not installed"
    )
    @patch('MetaTrader5.history_deals_get')
    def test_export_excel(self, mock_deals_get, mt5_history, sample_deals):
        """Test exporting to Excel."""
        mock_deals_get.return_value = sample_deals

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "history.xlsx"
            result = mt5_history.export(filepath, 'deals', format='excel')

            assert result is True
            assert filepath.exists()

    @patch('MetaTrader5.history_deals_get')
    def test_export_no_data(self, mock_deals_get, mt5_history):
        """Test export with no data."""
        mock_deals_get.return_value = ()

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "history.csv"
            result = mt5_history.export(filepath, 'deals')

            assert result is False


class TestSummary:
    """Test summary methods."""

    def test_get_summary(self, mt5_history, sample_deals_df):
        """Test getting summary."""
        result = mt5_history.get_summary(deals=sample_deals_df)

        assert isinstance(result, dict)
        assert 'total_trades' in result
        assert 'total_profit' in result
        assert 'win_rate' in result
        assert 'date_range' in result
        assert 'symbols_traded' in result
        assert result['total_trades'] == 5
        assert result['symbols_traded'] == 2

    def test_get_summary_empty(self, mt5_history):
        """Test summary with no deals."""
        result = mt5_history.get_summary(deals=pd.DataFrame())

        assert isinstance(result, dict)
        assert result['total_trades'] == 0
        assert 'message' in result

    @patch('MetaTrader5.history_deals_get')
    def test_print_report(self, mock_deals_get, mt5_history, sample_deals, capsys):
        """Test printing report."""
        mock_deals_get.return_value = sample_deals

        mt5_history.print_report('summary')

        captured = capsys.readouterr()
        assert len(captured.out) > 0


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_calculate_profit_factor_no_losses(self, mt5_history):
        """Test profit factor with only winning trades."""
        df = pd.DataFrame({
            'profit': [100, 200, 150],
            'commission': [0, 0, 0],
            'swap': [0, 0, 0]
        })

        result = mt5_history.calculate('profit_factor', deals=df)
        assert result == float('inf')

    def test_calculate_win_rate_no_trades(self, mt5_history):
        """Test win rate with no trades."""
        df = pd.DataFrame()

        result = mt5_history.calculate('win_rate', deals=df)
        assert result is None

    @patch('MetaTrader5.history_deals_get')
    def test_get_with_date_strings(self, mock_deals_get, mt5_history, sample_deals):
        """Test getting deals with string dates."""
        mock_deals_get.return_value = sample_deals

        result = mt5_history.get('deals', start='2021-12-01', end='2021-12-31')

        assert isinstance(result, pd.DataFrame)

    def test_analyze_missing_column(self, mt5_history):
        """Test analysis with missing required column."""
        df = pd.DataFrame({'profit': [100, -50]})

        result = mt5_history.analyze('by_symbol', deals=df)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
