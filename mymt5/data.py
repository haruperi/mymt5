from mylogger import logger
"""
MT5Data - Market data retrieval and management for MetaTrader 5.

This module provides comprehensive functionality for retrieving, processing,
and managing market data including OHLCV bars, ticks, streaming data, and more.
"""

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Union, Dict, List, Callable, Any, Tuple
from pathlib import Path
import json
import pickle
import threading
import time

from .enums import TimeFrame
from .utils import MT5Utils


class MT5Data:
    """
    Market data retrieval and management class.

    Provides methods for:
    - OHLCV bar data retrieval
    - Tick data retrieval
    - Real-time data streaming
    - Data processing and cleaning
    - Caching mechanisms
    - Export to various formats
    """

    def __init__(self, client=None):
        """
        Initialize MT5Data instance.

        Args:
            client: MT5Client instance for connection management (optional)
        """
        self.client = client
        self._cache: Dict[str, Any] = {}
        self._stream_threads: Dict[str, threading.Thread] = {}
        self._stream_active: Dict[str, bool] = {}
        self._stream_callbacks: Dict[str, Callable] = {}

        logger.info("MT5Data initialized")

    def get_bars(
        self,
        symbol: str,
        timeframe: Union[TimeFrame, int],
        count: Optional[int] = None,
        start: Optional[Union[datetime, str]] = None,
        end: Optional[Union[datetime, str]] = None,
        as_dataframe: bool = True
    ) -> Union[pd.DataFrame, List[Dict], None]:
        """
        Retrieve OHLCV bar data for a symbol.

        Args:
            symbol: Trading symbol (e.g., "EURUSD")
            timeframe: Timeframe for bars (TimeFrame enum or MT5 constant)
            count: Number of bars to retrieve (if start/end not provided)
            start: Start date/time for data retrieval
            end: End date/time for data retrieval
            as_dataframe: Return as DataFrame (True) or list of dicts (False)

        Returns:
            DataFrame or list of dicts containing OHLCV data, or None on error

        Examples:
            >>> data = mt5_data.get_bars("EURUSD", TimeFrame.H1, count=100)
            >>> data = mt5_data.get_bars("EURUSD", TimeFrame.D1,
            ...                          start="2024-01-01", end="2024-12-31")
        """
        try:
            # Convert timeframe to MT5 constant
            if isinstance(timeframe, TimeFrame):
                tf = timeframe.value
            else:
                tf = timeframe

            # Get bars based on parameters
            if count is not None:
                # Get by count
                rates = mt5.copy_rates_from_pos(symbol, tf, 0, count)
                logger.info(f"Retrieved {len(rates) if rates is not None else 0} bars for {symbol} {timeframe}")
            elif start is not None and end is not None:
                # Convert dates if needed
                if isinstance(start, str):
                    start = pd.to_datetime(start)
                if isinstance(end, str):
                    end = pd.to_datetime(end)

                rates = mt5.copy_rates_range(symbol, tf, start, end)
                logger.info(f"Retrieved {len(rates) if rates is not None else 0} bars for {symbol} from {start} to {end}")
            elif start is not None:
                # Get from start date to now
                if isinstance(start, str):
                    start = pd.to_datetime(start)

                rates = mt5.copy_rates_from(symbol, tf, start, count or 100000)
                logger.info(f"Retrieved {len(rates) if rates is not None else 0} bars for {symbol} from {start}")
            else:
                logger.error("Must provide either count or start/end parameters")
                return None

            if rates is None or len(rates) == 0:
                error = mt5.last_error()
                logger.error(f"Failed to retrieve bars: {error}")
                return None

            # Convert to DataFrame or dict
            if as_dataframe:
                df = pd.DataFrame(rates)
                df['time'] = pd.to_datetime(df['time'], unit='s')
                return df
            else:
                return [dict(zip(rates.dtype.names, row)) for row in rates]

        except Exception as e:
            logger.error(f"Error retrieving bars: {e}")
            return None

    def get_ticks(
        self,
        symbol: str,
        count: Optional[int] = None,
        start: Optional[Union[datetime, str]] = None,
        end: Optional[Union[datetime, str]] = None,
        flags: int = mt5.COPY_TICKS_ALL,
        as_dataframe: bool = True
    ) -> Union[pd.DataFrame, List[Dict], None]:
        """
        Retrieve tick data for a symbol.

        Args:
            symbol: Trading symbol
            count: Number of ticks to retrieve
            start: Start date/time
            end: End date/time
            flags: Tick flags (COPY_TICKS_ALL, COPY_TICKS_INFO, COPY_TICKS_TRADE)
            as_dataframe: Return as DataFrame (True) or list of dicts (False)

        Returns:
            DataFrame or list of dicts containing tick data, or None on error

        Examples:
            >>> ticks = mt5_data.get_ticks("EURUSD", count=1000)
            >>> ticks = mt5_data.get_ticks("EURUSD",
            ...                            start="2024-01-01",
            ...                            flags=mt5.COPY_TICKS_TRADE)
        """
        try:
            # Get ticks based on parameters
            if count is not None and start is None:
                # Get last N ticks
                ticks = mt5.copy_ticks_from(symbol, datetime.now(), count, flags)
                logger.info(f"Retrieved {len(ticks) if ticks is not None else 0} ticks for {symbol}")
            elif start is not None and end is not None:
                # Get ticks in date range
                if isinstance(start, str):
                    start = pd.to_datetime(start)
                if isinstance(end, str):
                    end = pd.to_datetime(end)

                ticks = mt5.copy_ticks_range(symbol, start, end, flags)
                logger.info(f"Retrieved {len(ticks) if ticks is not None else 0} ticks for {symbol} from {start} to {end}")
            elif start is not None:
                # Get from start date
                if isinstance(start, str):
                    start = pd.to_datetime(start)

                ticks = mt5.copy_ticks_from(symbol, start, count or 100000, flags)
                logger.info(f"Retrieved {len(ticks) if ticks is not None else 0} ticks for {symbol} from {start}")
            else:
                logger.error("Must provide either count or start/end parameters")
                return None

            if ticks is None or len(ticks) == 0:
                error = mt5.last_error()
                logger.error(f"Failed to retrieve ticks: {error}")
                return None

            # Convert to DataFrame or dict
            if as_dataframe:
                df = pd.DataFrame(ticks)
                df['time'] = pd.to_datetime(df['time'], unit='s')
                if 'time_msc' in df.columns:
                    df['time_msc'] = pd.to_datetime(df['time_msc'], unit='ms')
                return df
            else:
                return [dict(zip(ticks.dtype.names, row)) for row in ticks]

        except Exception as e:
            logger.error(f"Error retrieving ticks: {e}")
            return None

    def stream(
        self,
        symbol: str,
        data_type: str = "ticks",
        callback: Optional[Callable] = None,
        interval: float = 1.0,
        timeframe: Optional[Union[TimeFrame, int]] = None
    ) -> bool:
        """
        Start streaming real-time data.

        Args:
            symbol: Trading symbol
            data_type: Type of data to stream ("ticks" or "bars")
            callback: Function to call with new data
            interval: Update interval in seconds (for bars)
            timeframe: Timeframe for bars (required if data_type="bars")

        Returns:
            True if streaming started successfully, False otherwise

        Examples:
            >>> def on_tick(data):
            ...     print(f"New tick: {data}")
            >>> mt5_data.stream("EURUSD", "ticks", on_tick)
        """
        try:
            stream_id = f"{symbol}_{data_type}"

            # Check if already streaming
            if stream_id in self._stream_active and self._stream_active[stream_id]:
                logger.warning(f"Already streaming {data_type} for {symbol}")
                return False

            # Store callback
            self._stream_callbacks[stream_id] = callback
            self._stream_active[stream_id] = True

            # Start streaming thread
            if data_type == "ticks":
                thread = threading.Thread(
                    target=self._stream_ticks,
                    args=(symbol, stream_id),
                    daemon=True
                )
            elif data_type == "bars":
                if timeframe is None:
                    logger.error("Timeframe required for bar streaming")
                    return False

                thread = threading.Thread(
                    target=self._stream_bars,
                    args=(symbol, timeframe, interval, stream_id),
                    daemon=True
                )
            else:
                logger.error(f"Invalid data type: {data_type}")
                return False

            self._stream_threads[stream_id] = thread
            thread.start()

            logger.info(f"Started streaming {data_type} for {symbol}")
            return True

        except Exception as e:
            logger.error(f"Error starting stream: {e}")
            return False

    def stop_stream(self, symbol: str, data_type: str = "ticks") -> bool:
        """
        Stop streaming data for a symbol.

        Args:
            symbol: Trading symbol
            data_type: Type of data being streamed

        Returns:
            True if stopped successfully, False otherwise
        """
        try:
            stream_id = f"{symbol}_{data_type}"

            if stream_id not in self._stream_active:
                logger.warning(f"No active stream for {symbol} {data_type}")
                return False

            # Stop the stream
            self._stream_active[stream_id] = False

            # Wait for thread to finish (with timeout)
            if stream_id in self._stream_threads:
                self._stream_threads[stream_id].join(timeout=5.0)
                del self._stream_threads[stream_id]

            # Clean up
            if stream_id in self._stream_callbacks:
                del self._stream_callbacks[stream_id]

            logger.info(f"Stopped streaming {data_type} for {symbol}")
            return True

        except Exception as e:
            logger.error(f"Error stopping stream: {e}")
            return False

    def _stream_ticks(self, symbol: str, stream_id: str):
        """Internal method to stream ticks."""
        last_tick_time = 0

        while self._stream_active.get(stream_id, False):
            try:
                # Get latest tick
                tick = mt5.symbol_info_tick(symbol)

                if tick and tick.time > last_tick_time:
                    last_tick_time = tick.time

                    # Call callback if provided
                    if stream_id in self._stream_callbacks:
                        callback = self._stream_callbacks[stream_id]
                        if callback:
                            tick_dict = {
                                'time': datetime.fromtimestamp(tick.time),
                                'bid': tick.bid,
                                'ask': tick.ask,
                                'last': tick.last,
                                'volume': tick.volume
                            }
                            callback(tick_dict)

                time.sleep(0.1)  # Small delay to avoid CPU overuse

            except Exception as e:
                logger.error(f"Error in tick stream: {e}")
                time.sleep(1)

    def _stream_bars(self, symbol: str, timeframe: Union[TimeFrame, int], interval: float, stream_id: str):
        """Internal method to stream bars."""
        last_bar_time = 0

        # Convert timeframe
        if isinstance(timeframe, TimeFrame):
            tf = timeframe.value
        else:
            tf = timeframe

        while self._stream_active.get(stream_id, False):
            try:
                # Get latest bar
                rates = mt5.copy_rates_from_pos(symbol, tf, 0, 1)

                if rates is not None and len(rates) > 0:
                    bar = rates[0]

                    if bar['time'] > last_bar_time:
                        last_bar_time = bar['time']

                        # Call callback if provided
                        if stream_id in self._stream_callbacks:
                            callback = self._stream_callbacks[stream_id]
                            if callback:
                                bar_dict = {
                                    'time': datetime.fromtimestamp(bar['time']),
                                    'open': bar['open'],
                                    'high': bar['high'],
                                    'low': bar['low'],
                                    'close': bar['close'],
                                    'volume': bar['tick_volume']
                                }
                                callback(bar_dict)

                time.sleep(interval)

            except Exception as e:
                logger.error(f"Error in bar stream: {e}")
                time.sleep(interval)

    def process(
        self,
        data: pd.DataFrame,
        operation: str,
        **kwargs
    ) -> Optional[pd.DataFrame]:
        """
        Process and transform market data.

        Args:
            data: DataFrame containing market data
            operation: Type of operation to perform
                      ('normalize', 'clean', 'resample', 'fill_missing', 'detect_gaps')
            **kwargs: Additional parameters for the operation

        Returns:
            Processed DataFrame or None on error

        Examples:
            >>> clean_data = mt5_data.process(data, 'clean')
            >>> resampled = mt5_data.process(data, 'resample', timeframe='4H')
        """
        try:
            if operation == 'normalize':
                return self._normalize_data(data, **kwargs)
            elif operation == 'clean':
                return self._clean_data(data, **kwargs)
            elif operation == 'resample':
                return self._resample_data(data, **kwargs)
            elif operation == 'fill_missing':
                return self._fill_missing(data, **kwargs)
            elif operation == 'detect_gaps':
                return self._detect_gaps(data, **kwargs)
            else:
                logger.error(f"Unknown operation: {operation}")
                return None

        except Exception as e:
            logger.error(f"Error processing data: {e}")
            return None

    def _normalize_data(self, data: pd.DataFrame, method: str = 'minmax') -> pd.DataFrame:
        """Normalize price data."""
        df = data.copy()

        price_cols = ['open', 'high', 'low', 'close']
        available_cols = [col for col in price_cols if col in df.columns]

        if method == 'minmax':
            for col in available_cols:
                min_val = df[col].min()
                max_val = df[col].max()
                df[f'{col}_normalized'] = (df[col] - min_val) / (max_val - min_val)
        elif method == 'zscore':
            for col in available_cols:
                df[f'{col}_normalized'] = (df[col] - df[col].mean()) / df[col].std()

        logger.info(f"Normalized data using {method} method")
        return df

    def _clean_data(self, data: pd.DataFrame, remove_duplicates: bool = True) -> pd.DataFrame:
        """Clean market data by removing duplicates and invalid values."""
        df = data.copy()

        # Remove duplicates
        if remove_duplicates and 'time' in df.columns:
            df = df.drop_duplicates(subset=['time'], keep='last')

        # Remove rows with NaN in critical columns
        critical_cols = ['open', 'high', 'low', 'close']
        available_cols = [col for col in critical_cols if col in df.columns]
        df = df.dropna(subset=available_cols)

        # Remove rows with invalid prices (zero or negative)
        for col in available_cols:
            df = df[df[col] > 0]

        logger.info(f"Cleaned data: {len(data)} -> {len(df)} rows")
        return df

    def _resample_data(self, data: pd.DataFrame, timeframe: str = '1H') -> pd.DataFrame:
        """Resample OHLCV data to different timeframe."""
        if 'time' not in data.columns:
            logger.error("Data must have 'time' column for resampling")
            return data

        df = data.copy()
        df = df.set_index('time')

        # Resample OHLCV
        resampled = pd.DataFrame()

        if 'open' in df.columns:
            resampled['open'] = df['open'].resample(timeframe).first()
        if 'high' in df.columns:
            resampled['high'] = df['high'].resample(timeframe).max()
        if 'low' in df.columns:
            resampled['low'] = df['low'].resample(timeframe).min()
        if 'close' in df.columns:
            resampled['close'] = df['close'].resample(timeframe).last()
        if 'volume' in df.columns or 'tick_volume' in df.columns:
            vol_col = 'volume' if 'volume' in df.columns else 'tick_volume'
            resampled['volume'] = df[vol_col].resample(timeframe).sum()

        resampled = resampled.dropna()
        resampled = resampled.reset_index()

        logger.info(f"Resampled data to {timeframe}")
        return resampled

    def _fill_missing(self, data: pd.DataFrame, method: str = 'ffill') -> pd.DataFrame:
        """Fill missing values in data."""
        df = data.copy()

        if method == 'ffill':
            df = df.ffill()
        elif method == 'bfill':
            df = df.bfill()
        elif method == 'interpolate':
            df = df.interpolate(method='linear')
        elif method == 'zero':
            df = df.fillna(0)

        logger.info(f"Filled missing values using {method} method")
        return df

    def _detect_gaps(self, data: pd.DataFrame, timeframe_minutes: int = 60) -> pd.DataFrame:
        """Detect gaps in time series data."""
        if 'time' not in data.columns:
            logger.error("Data must have 'time' column for gap detection")
            return pd.DataFrame()

        df = data.copy()
        df = df.sort_values('time')

        # Calculate time differences
        df['time_diff'] = df['time'].diff()

        # Expected difference
        expected_diff = timedelta(minutes=timeframe_minutes)

        # Find gaps (where difference is greater than expected)
        gaps = df[df['time_diff'] > expected_diff * 1.5]

        logger.info(f"Detected {len(gaps)} gaps in data")
        return gaps[['time', 'time_diff']]

    def cache(self, key: str, data: Any, ttl: Optional[int] = None):
        """
        Cache data with optional time-to-live.

        Args:
            key: Cache key
            data: Data to cache
            ttl: Time to live in seconds (None for no expiration)
        """
        self._cache[key] = {
            'data': data,
            'timestamp': datetime.now(),
            'ttl': ttl
        }
        logger.debug(f"Cached data with key: {key}")

    def get_cached(self, key: str) -> Optional[Any]:
        """
        Retrieve cached data.

        Args:
            key: Cache key

        Returns:
            Cached data or None if not found/expired
        """
        if key not in self._cache:
            return None

        cache_entry = self._cache[key]

        # Check if expired
        if cache_entry['ttl'] is not None:
            age = (datetime.now() - cache_entry['timestamp']).total_seconds()
            if age > cache_entry['ttl']:
                del self._cache[key]
                logger.debug(f"Cache expired for key: {key}")
                return None

        logger.debug(f"Retrieved cached data for key: {key}")
        return cache_entry['data']

    def clear_cache(self, key: Optional[str] = None):
        """
        Clear cache.

        Args:
            key: Specific key to clear (None to clear all)
        """
        if key is None:
            self._cache.clear()
            logger.info("Cleared all cache")
        elif key in self._cache:
            del self._cache[key]
            logger.info(f"Cleared cache for key: {key}")

    def export(
        self,
        data: pd.DataFrame,
        filepath: Union[str, Path],
        format: str = 'csv',
        **kwargs
    ) -> bool:
        """
        Export data to file.

        Args:
            data: DataFrame to export
            filepath: Output file path
            format: Export format ('csv', 'json', 'parquet', 'pickle')
            **kwargs: Additional parameters for export

        Returns:
            True if successful, False otherwise

        Examples:
            >>> mt5_data.export(data, 'eurusd_data.csv', format='csv')
            >>> mt5_data.export(data, 'data.parquet', format='parquet')
        """
        try:
            filepath = Path(filepath)
            filepath.parent.mkdir(parents=True, exist_ok=True)

            if format == 'csv':
                data.to_csv(filepath, index=False, **kwargs)
            elif format == 'json':
                data.to_json(filepath, orient='records', date_format='iso', **kwargs)
            elif format == 'parquet':
                data.to_parquet(filepath, **kwargs)
            elif format == 'pickle':
                data.to_pickle(filepath, **kwargs)
            else:
                logger.error(f"Unsupported format: {format}")
                return False

            logger.info(f"Exported data to {filepath} ({format})")
            return True

        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            return False

    def get_timeframes(self) -> List[Dict[str, Any]]:
        """
        Get available timeframes.

        Returns:
            List of timeframe information
        """
        timeframes = []
        for tf in TimeFrame:
            timeframes.append({
                'name': tf.name,
                'value': tf.value,
                'minutes': self._timeframe_to_minutes(tf)
            })
        return timeframes

    def convert_timeframe(self, timeframe: Union[str, int, TimeFrame]) -> int:
        """
        Convert timeframe to MT5 constant.

        Args:
            timeframe: Timeframe as string, enum, or int

        Returns:
            MT5 timeframe constant
        """
        if isinstance(timeframe, int):
            return timeframe
        elif isinstance(timeframe, TimeFrame):
            return timeframe.value
        elif isinstance(timeframe, str):
            try:
                return TimeFrame[timeframe.upper()].value
            except KeyError:
                logger.error(f"Invalid timeframe: {timeframe}")
                return mt5.TIMEFRAME_H1
        return mt5.TIMEFRAME_H1

    def _timeframe_to_minutes(self, timeframe: Union[TimeFrame, int]) -> int:
        """Convert timeframe to minutes."""
        if isinstance(timeframe, TimeFrame):
            tf = timeframe.value
        else:
            tf = timeframe

        timeframe_map = {
            mt5.TIMEFRAME_M1: 1,
            mt5.TIMEFRAME_M5: 5,
            mt5.TIMEFRAME_M15: 15,
            mt5.TIMEFRAME_M30: 30,
            mt5.TIMEFRAME_H1: 60,
            mt5.TIMEFRAME_H4: 240,
            mt5.TIMEFRAME_D1: 1440,
            mt5.TIMEFRAME_W1: 10080,
            mt5.TIMEFRAME_MN1: 43200
        }

        return timeframe_map.get(tf, 60)

    def get_summary(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Get summary statistics for data.

        Args:
            data: DataFrame containing market data

        Returns:
            Dictionary with summary statistics
        """
        summary = {
            'rows': len(data),
            'columns': list(data.columns),
            'missing_values': data.isnull().sum().to_dict(),
            'date_range': None,
            'price_stats': {}
        }

        # Date range
        if 'time' in data.columns:
            summary['date_range'] = {
                'start': data['time'].min(),
                'end': data['time'].max(),
                'duration': data['time'].max() - data['time'].min()
            }

        # Price statistics
        price_cols = ['open', 'high', 'low', 'close']
        for col in price_cols:
            if col in data.columns:
                summary['price_stats'][col] = {
                    'min': float(data[col].min()),
                    'max': float(data[col].max()),
                    'mean': float(data[col].mean()),
                    'std': float(data[col].std())
                }

        return summary

    def calculate_stats(self, data: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate statistical measures for market data.

        Args:
            data: DataFrame containing market data

        Returns:
            Dictionary with calculated statistics
        """
        stats = {}

        if 'close' in data.columns:
            prices = data['close']

            # Returns
            returns = prices.pct_change().dropna()

            stats['total_return'] = float((prices.iloc[-1] / prices.iloc[0] - 1) * 100)
            stats['volatility'] = float(returns.std() * np.sqrt(252) * 100)
            stats['sharpe_ratio'] = float(returns.mean() / returns.std() * np.sqrt(252)) if returns.std() > 0 else 0

            # Drawdown
            cumulative = (1 + returns).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            stats['max_drawdown'] = float(drawdown.min() * 100)

            # Price range
            stats['price_range'] = float(prices.max() - prices.min())
            stats['price_range_pct'] = float((prices.max() / prices.min() - 1) * 100)

        return stats
