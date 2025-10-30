from mylogger import logger
"""
MT5History - Historical trading data and performance analysis for MetaTrader 5.

This module provides comprehensive functionality for retrieving and analyzing
historical trading data including deals, orders, performance metrics, and reports.
"""

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Union, Dict, List, Any, Tuple
from pathlib import Path
import json

from .utils import MT5Utils


class MT5History:
    """
    Historical trading data and performance analysis class.

    Provides methods for:
    - Retrieving historical deals and orders
    - Calculating performance metrics
    - Analyzing trading patterns
    - Generating reports
    """

    def __init__(self, client=None):
        """
        Initialize MT5History instance.

        Args:
            client: MT5Client instance for connection management (optional)
        """
        self.client = client
        self._cache: Dict[str, Any] = {}

        logger.info("MT5History initialized")

    def get(
        self,
        data_type: str = 'deals',
        start: Optional[Union[datetime, str]] = None,
        end: Optional[Union[datetime, str]] = None,
        symbol: Optional[str] = None,
        ticket: Optional[int] = None,
        position: Optional[int] = None,
        as_dataframe: bool = True
    ) -> Union[pd.DataFrame, List[Dict], None]:
        """
        Retrieve historical data (deals or orders).

        Args:
            data_type: Type of data ('deals', 'orders', or 'both')
            start: Start date/time (None for all history)
            end: End date/time (None for now)
            symbol: Filter by symbol
            ticket: Filter by ticket number
            position: Filter by position ID
            as_dataframe: Return as DataFrame (True) or list of dicts (False)

        Returns:
            DataFrame or list of dicts containing historical data, or None on error

        Examples:
            >>> history = mt5_history.get('deals', start='2024-01-01')
            >>> orders = mt5_history.get('orders', symbol='EURUSD')
            >>> both = mt5_history.get('both', start=datetime(2024, 1, 1))
        """
        try:
            # Convert dates if needed
            if isinstance(start, str):
                start = pd.to_datetime(start)
            if isinstance(end, str):
                end = pd.to_datetime(end)

            # Default to last 30 days if no dates provided
            if start is None:
                start = datetime.now() - timedelta(days=30)
            if end is None:
                end = datetime.now()

            if data_type == 'deals':
                return self._fetch_deals(start, end, symbol, ticket, position, as_dataframe)
            elif data_type == 'orders':
                return self._fetch_orders(start, end, symbol, ticket, position, as_dataframe)
            elif data_type == 'both':
                deals = self._fetch_deals(start, end, symbol, ticket, position, as_dataframe)
                orders = self._fetch_orders(start, end, symbol, ticket, position, as_dataframe)
                return {'deals': deals, 'orders': orders}
            else:
                logger.error(f"Invalid data type: {data_type}")
                return None

        except Exception as e:
            logger.error(f"Error retrieving history: {e}")
            return None

    def _fetch_deals(
        self,
        start: datetime,
        end: datetime,
        symbol: Optional[str] = None,
        ticket: Optional[int] = None,
        position: Optional[int] = None,
        as_dataframe: bool = True
    ) -> Union[pd.DataFrame, List[Dict], None]:
        """Internal method to fetch deals."""
        try:
            # Get deals based on parameters
            if ticket:
                deals = mt5.history_deals_get(ticket=ticket)
            elif position:
                deals = mt5.history_deals_get(position=position)
            else:
                deals = mt5.history_deals_get(start, end)

            if deals is None or len(deals) == 0:
                logger.info("No deals found in the specified period")
                return pd.DataFrame() if as_dataframe else []

            # Convert to DataFrame
            df = pd.DataFrame(list(deals), columns=deals[0]._asdict().keys())

            # Filter by symbol if specified
            if symbol:
                df = df[df['symbol'] == symbol]

            # Convert timestamps
            df['time'] = pd.to_datetime(df['time'], unit='s')

            logger.info(f"Retrieved {len(df)} deals")

            if as_dataframe:
                return df
            else:
                return df.to_dict('records')

        except Exception as e:
            logger.error(f"Error fetching deals: {e}")
            return None

    def _fetch_orders(
        self,
        start: datetime,
        end: datetime,
        symbol: Optional[str] = None,
        ticket: Optional[int] = None,
        position: Optional[int] = None,
        as_dataframe: bool = True
    ) -> Union[pd.DataFrame, List[Dict], None]:
        """Internal method to fetch orders."""
        try:
            # Get orders based on parameters
            if ticket:
                orders = mt5.history_orders_get(ticket=ticket)
            elif position:
                orders = mt5.history_orders_get(position=position)
            else:
                orders = mt5.history_orders_get(start, end)

            if orders is None or len(orders) == 0:
                logger.info("No orders found in the specified period")
                return pd.DataFrame() if as_dataframe else []

            # Convert to DataFrame
            df = pd.DataFrame(list(orders), columns=orders[0]._asdict().keys())

            # Filter by symbol if specified
            if symbol:
                df = df[df['symbol'] == symbol]

            # Convert timestamps
            df['time_setup'] = pd.to_datetime(df['time_setup'], unit='s')
            if 'time_done' in df.columns:
                df['time_done'] = pd.to_datetime(df['time_done'], unit='s')

            logger.info(f"Retrieved {len(df)} orders")

            if as_dataframe:
                return df
            else:
                return df.to_dict('records')

        except Exception as e:
            logger.error(f"Error fetching orders: {e}")
            return None

    def get_today(self, data_type: str = 'deals') -> Union[pd.DataFrame, Dict, None]:
        """
        Get today's deals or orders.

        Args:
            data_type: Type of data ('deals', 'orders', or 'both')

        Returns:
            DataFrame or dict containing today's data

        Examples:
            >>> today_deals = mt5_history.get_today('deals')
            >>> today_orders = mt5_history.get_today('orders')
        """
        start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end = datetime.now()

        return self.get(data_type, start, end)

    def get_period(
        self,
        period: str = 'day',
        data_type: str = 'deals'
    ) -> Union[pd.DataFrame, Dict, None]:
        """
        Get data for a specific period.

        Args:
            period: Time period ('day', 'week', 'month', 'year')
            data_type: Type of data ('deals', 'orders', or 'both')

        Returns:
            DataFrame or dict containing period data

        Examples:
            >>> week_deals = mt5_history.get_period('week', 'deals')
            >>> month_orders = mt5_history.get_period('month', 'orders')
        """
        now = datetime.now()

        if period == 'day':
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == 'week':
            start = now - timedelta(days=now.weekday())
            start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == 'month':
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif period == 'year':
            start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            logger.error(f"Invalid period: {period}")
            return None

        return self.get(data_type, start, now)

    def calculate(
        self,
        metric: str,
        deals: Optional[pd.DataFrame] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None
    ) -> Union[float, Dict[str, float], None]:
        """
        Calculate performance metrics.

        Args:
            metric: Metric to calculate ('win_rate', 'profit_factor', 'avg_win',
                   'avg_loss', 'largest_win', 'largest_loss', 'sharpe_ratio',
                   'max_drawdown', 'total_trades', 'total_profit',
                   'total_commission', 'total_swap', 'all')
            deals: DataFrame of deals (if None, will fetch)
            start: Start date for analysis
            end: End date for analysis

        Returns:
            Calculated metric value or dict of all metrics

        Examples:
            >>> win_rate = mt5_history.calculate('win_rate')
            >>> profit_factor = mt5_history.calculate('profit_factor')
            >>> all_metrics = mt5_history.calculate('all')
        """
        try:
            # Fetch deals if not provided
            if deals is None:
                deals = self.get('deals', start, end)

            if deals is None or len(deals) == 0:
                logger.warning("No deals available for calculation")
                return None

            # Calculate requested metric
            if metric == 'win_rate':
                return self._calculate_win_rate(deals)
            elif metric == 'profit_factor':
                return self._calculate_profit_factor(deals)
            elif metric == 'avg_win':
                return self._calculate_avg_win(deals)
            elif metric == 'avg_loss':
                return self._calculate_avg_loss(deals)
            elif metric == 'largest_win':
                return self._calculate_largest_win(deals)
            elif metric == 'largest_loss':
                return self._calculate_largest_loss(deals)
            elif metric == 'sharpe_ratio':
                return self._calculate_sharpe_ratio(deals)
            elif metric == 'max_drawdown':
                return self._calculate_max_drawdown(deals)
            elif metric == 'total_trades':
                return len(deals)
            elif metric == 'total_profit':
                return float(deals['profit'].sum())
            elif metric == 'total_commission':
                return float(deals['commission'].sum()) if 'commission' in deals.columns else 0.0
            elif metric == 'total_swap':
                return float(deals['swap'].sum()) if 'swap' in deals.columns else 0.0
            elif metric == 'all':
                return self._calculate_all_metrics(deals)
            else:
                logger.error(f"Unknown metric: {metric}")
                return None

        except Exception as e:
            logger.error(f"Error calculating metric: {e}")
            return None

    def _calculate_win_rate(self, deals: pd.DataFrame) -> float:
        """Calculate win rate percentage."""
        if len(deals) == 0:
            return 0.0

        winning_trades = len(deals[deals['profit'] > 0])
        return (winning_trades / len(deals)) * 100

    def _calculate_profit_factor(self, deals: pd.DataFrame) -> float:
        """Calculate profit factor."""
        if len(deals) == 0:
            return 0.0

        gross_profit = deals[deals['profit'] > 0]['profit'].sum()
        gross_loss = abs(deals[deals['profit'] < 0]['profit'].sum())

        if gross_loss == 0:
            return float('inf') if gross_profit > 0 else 0.0

        return gross_profit / gross_loss

    def _calculate_avg_win(self, deals: pd.DataFrame) -> float:
        """Calculate average winning trade."""
        winning_trades = deals[deals['profit'] > 0]
        if len(winning_trades) == 0:
            return 0.0

        return float(winning_trades['profit'].mean())

    def _calculate_avg_loss(self, deals: pd.DataFrame) -> float:
        """Calculate average losing trade."""
        losing_trades = deals[deals['profit'] < 0]
        if len(losing_trades) == 0:
            return 0.0

        return float(losing_trades['profit'].mean())

    def _calculate_largest_win(self, deals: pd.DataFrame) -> float:
        """Calculate largest winning trade."""
        if len(deals) == 0:
            return 0.0

        return float(deals['profit'].max())

    def _calculate_largest_loss(self, deals: pd.DataFrame) -> float:
        """Calculate largest losing trade."""
        if len(deals) == 0:
            return 0.0

        return float(deals['profit'].min())

    def _calculate_sharpe_ratio(self, deals: pd.DataFrame, risk_free_rate: float = 0.0) -> float:
        """Calculate Sharpe ratio."""
        if len(deals) == 0:
            return 0.0

        returns = deals['profit']
        if returns.std() == 0:
            return 0.0

        return float((returns.mean() - risk_free_rate) / returns.std())

    def _calculate_max_drawdown(self, deals: pd.DataFrame) -> float:
        """Calculate maximum drawdown."""
        if len(deals) == 0:
            return 0.0

        # Calculate cumulative profit
        deals_sorted = deals.sort_values('time')
        cumulative_profit = deals_sorted['profit'].cumsum()

        # Calculate running maximum
        running_max = cumulative_profit.expanding().max()

        # Calculate drawdown
        drawdown = cumulative_profit - running_max

        return float(drawdown.min())

    def _calculate_all_metrics(self, deals: pd.DataFrame) -> Dict[str, float]:
        """Calculate all performance metrics."""
        return {
            'total_trades': len(deals),
            'win_rate': self._calculate_win_rate(deals),
            'profit_factor': self._calculate_profit_factor(deals),
            'total_profit': float(deals['profit'].sum()),
            'avg_win': self._calculate_avg_win(deals),
            'avg_loss': self._calculate_avg_loss(deals),
            'largest_win': self._calculate_largest_win(deals),
            'largest_loss': self._calculate_largest_loss(deals),
            'sharpe_ratio': self._calculate_sharpe_ratio(deals),
            'max_drawdown': self._calculate_max_drawdown(deals),
            'total_commission': float(deals['commission'].sum()) if 'commission' in deals.columns else 0.0,
            'total_swap': float(deals['swap'].sum()) if 'swap' in deals.columns else 0.0,
        }

    def analyze(
        self,
        analysis_type: str,
        deals: Optional[pd.DataFrame] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None
    ) -> Union[pd.DataFrame, Dict, None]:
        """
        Analyze trading patterns.

        Args:
            analysis_type: Type of analysis ('by_symbol', 'by_hour', 'by_day',
                          'by_weekday', 'by_month', 'winning_trades',
                          'losing_trades', 'statistics')
            deals: DataFrame of deals (if None, will fetch)
            start: Start date for analysis
            end: End date for analysis

        Returns:
            Analysis results as DataFrame or dict

        Examples:
            >>> by_symbol = mt5_history.analyze('by_symbol')
            >>> by_hour = mt5_history.analyze('by_hour')
            >>> winners = mt5_history.analyze('winning_trades')
        """
        try:
            # Fetch deals if not provided
            if deals is None:
                deals = self.get('deals', start, end)

            if deals is None or len(deals) == 0:
                logger.warning("No deals available for analysis")
                return None

            if analysis_type == 'by_symbol':
                return self._analyze_by_symbol(deals)
            elif analysis_type == 'by_hour':
                return self._analyze_by_time(deals, 'hour')
            elif analysis_type == 'by_day':
                return self._analyze_by_time(deals, 'day')
            elif analysis_type == 'by_weekday':
                return self._analyze_by_time(deals, 'weekday')
            elif analysis_type == 'by_month':
                return self._analyze_by_time(deals, 'month')
            elif analysis_type == 'winning_trades':
                return deals[deals['profit'] > 0]
            elif analysis_type == 'losing_trades':
                return deals[deals['profit'] < 0]
            elif analysis_type == 'statistics':
                return self._calculate_all_metrics(deals)
            else:
                logger.error(f"Unknown analysis type: {analysis_type}")
                return None

        except Exception as e:
            logger.error(f"Error analyzing data: {e}")
            return None

    def _analyze_by_symbol(self, deals: pd.DataFrame) -> pd.DataFrame:
        """Analyze performance by symbol."""
        if 'symbol' not in deals.columns:
            logger.error("Deals DataFrame missing 'symbol' column")
            return pd.DataFrame()

        analysis = deals.groupby('symbol').agg({
            'profit': ['count', 'sum', 'mean', 'min', 'max'],
        }).round(2)

        analysis.columns = ['trades', 'total_profit', 'avg_profit', 'worst_trade', 'best_trade']
        analysis = analysis.reset_index()

        # Calculate win rate per symbol
        win_rates = []
        for symbol in analysis['symbol']:
            symbol_deals = deals[deals['symbol'] == symbol]
            win_rate = (len(symbol_deals[symbol_deals['profit'] > 0]) / len(symbol_deals)) * 100
            win_rates.append(win_rate)

        analysis['win_rate'] = win_rates

        return analysis.sort_values('total_profit', ascending=False)

    def _analyze_by_time(self, deals: pd.DataFrame, time_unit: str) -> pd.DataFrame:
        """Analyze performance by time period."""
        if 'time' not in deals.columns:
            logger.error("Deals DataFrame missing 'time' column")
            return pd.DataFrame()

        # Extract time unit
        if time_unit == 'hour':
            deals['time_unit'] = deals['time'].dt.hour
        elif time_unit == 'day':
            deals['time_unit'] = deals['time'].dt.day
        elif time_unit == 'weekday':
            deals['time_unit'] = deals['time'].dt.day_name()
        elif time_unit == 'month':
            deals['time_unit'] = deals['time'].dt.month_name()
        else:
            return pd.DataFrame()

        # Aggregate by time unit
        analysis = deals.groupby('time_unit').agg({
            'profit': ['count', 'sum', 'mean']
        }).round(2)

        analysis.columns = ['trades', 'total_profit', 'avg_profit']
        analysis = analysis.reset_index()

        return analysis.sort_values('time_unit')

    def generate_report(
        self,
        report_type: str = 'summary',
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        format: str = 'dict'
    ) -> Union[Dict, pd.DataFrame, str, None]:
        """
        Generate trading performance report.

        Args:
            report_type: Type of report ('performance', 'trade_log', 'summary', 'detailed')
            start: Start date for report
            end: End date for report
            format: Output format ('dict', 'dataframe', 'html', 'text')

        Returns:
            Report in requested format

        Examples:
            >>> report = mt5_history.generate_report('summary')
            >>> detailed = mt5_history.generate_report('detailed', format='dict')
        """
        try:
            deals = self.get('deals', start, end)

            if deals is None or len(deals) == 0:
                logger.warning("No deals available for report")
                return None

            if report_type == 'performance':
                report_data = self._calculate_all_metrics(deals)
            elif report_type == 'trade_log':
                report_data = deals
            elif report_type == 'summary':
                report_data = self.get_summary(deals)
            elif report_type == 'detailed':
                report_data = {
                    'metrics': self._calculate_all_metrics(deals),
                    'by_symbol': self._analyze_by_symbol(deals).to_dict('records'),
                    'by_hour': self._analyze_by_time(deals, 'hour').to_dict('records'),
                    'by_weekday': self._analyze_by_time(deals, 'weekday').to_dict('records'),
                }
            else:
                logger.error(f"Unknown report type: {report_type}")
                return None

            # Format report
            if format == 'dict':
                if isinstance(report_data, pd.DataFrame):
                    return report_data.to_dict('records')
                return report_data
            elif format == 'dataframe':
                if isinstance(report_data, dict):
                    return pd.DataFrame([report_data])
                return report_data
            elif format == 'html':
                return self._format_report_html(report_data, report_type)
            elif format == 'text':
                return self._format_report_text(report_data, report_type)
            else:
                logger.error(f"Unknown format: {format}")
                return None

        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return None

    def _format_report_html(self, data: Any, report_type: str) -> str:
        """Format report as HTML."""
        if isinstance(data, pd.DataFrame):
            return data.to_html()
        elif isinstance(data, dict):
            html = "<table border='1'>"
            for key, value in data.items():
                html += f"<tr><td><b>{key}</b></td><td>{value}</td></tr>"
            html += "</table>"
            return html
        return str(data)

    def _format_report_text(self, data: Any, report_type: str) -> str:
        """Format report as plain text."""
        if isinstance(data, pd.DataFrame):
            return data.to_string()
        elif isinstance(data, dict):
            text = f"\n{'='*60}\n{report_type.upper()} REPORT\n{'='*60}\n\n"
            for key, value in data.items():
                if isinstance(value, float):
                    text += f"{key}: {value:.2f}\n"
                else:
                    text += f"{key}: {value}\n"
            return text
        return str(data)

    def export(
        self,
        filepath: Union[str, Path],
        data_type: str = 'deals',
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        format: str = 'csv'
    ) -> bool:
        """
        Export historical data to file.

        Args:
            filepath: Output file path
            data_type: Type of data to export
            start: Start date
            end: End date
            format: Export format ('csv', 'json', 'excel')

        Returns:
            True if successful, False otherwise

        Examples:
            >>> mt5_history.export('history.csv', 'deals', format='csv')
            >>> mt5_history.export('orders.json', 'orders', format='json')
        """
        try:
            data = self.get(data_type, start, end)

            if data is None or (isinstance(data, pd.DataFrame) and len(data) == 0):
                logger.warning("No data to export")
                return False

            filepath = Path(filepath)
            filepath.parent.mkdir(parents=True, exist_ok=True)

            if isinstance(data, dict):
                # Export both deals and orders
                for key, df in data.items():
                    file_path = filepath.parent / f"{filepath.stem}_{key}{filepath.suffix}"
                    self._export_dataframe(df, file_path, format)
            else:
                self._export_dataframe(data, filepath, format)

            logger.info(f"Exported data to {filepath}")
            return True

        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            return False

    def _export_dataframe(self, df: pd.DataFrame, filepath: Path, format: str):
        """Export a single DataFrame."""
        if format == 'csv':
            df.to_csv(filepath, index=False)
        elif format == 'json':
            df.to_json(filepath, orient='records', date_format='iso')
        elif format == 'excel':
            df.to_excel(filepath, index=False)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def get_summary(
        self,
        deals: Optional[pd.DataFrame] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get summary of trading history.

        Args:
            deals: DataFrame of deals (if None, will fetch)
            start: Start date
            end: End date

        Returns:
            Dictionary with summary information

        Examples:
            >>> summary = mt5_history.get_summary()
            >>> print(summary)
        """
        if deals is None:
            deals = self.get('deals', start, end)

        if deals is None or len(deals) == 0:
            return {
                'total_trades': 0,
                'total_profit': 0.0,
                'message': 'No trading history available'
            }

        metrics = self._calculate_all_metrics(deals)

        # Add additional info
        if 'time' in deals.columns:
            metrics['date_range'] = {
                'start': deals['time'].min(),
                'end': deals['time'].max(),
                'duration_days': (deals['time'].max() - deals['time'].min()).days
            }

        if 'symbol' in deals.columns:
            metrics['symbols_traded'] = deals['symbol'].nunique()
            metrics['most_traded_symbol'] = deals['symbol'].value_counts().index[0]

        return metrics

    def print_report(
        self,
        report_type: str = 'summary',
        start: Optional[datetime] = None,
        end: Optional[datetime] = None
    ):
        """
        Print trading report to console.

        Args:
            report_type: Type of report to print
            start: Start date
            end: End date

        Examples:
            >>> mt5_history.print_report('summary')
            >>> mt5_history.print_report('detailed')
        """
        report = self.generate_report(report_type, start, end, format='text')

        if report:
            print(report)
        else:
            print("No data available for report")
