"""
MT5 Trading System - Utilities Module

This module provides utility functions for working with MT5 data, including time operations,
price/volume conversions, data formatting, file operations, and calculations.
"""

from mylogger import logger
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Union
import MetaTrader5 as mt5
import pandas as pd
import json
import pickle
import csv
from pathlib import Path


logger.info("Loading utils module")


class MT5Utils:
    """
    Static utility class providing helper methods for MT5 trading system.

    This class contains static methods for:
    - Time operations (conversions, formatting)
    - Price operations (conversions, formatting, rounding)
    - Volume operations (conversions, rounding)
    - Type conversions
    - Data formatting (dict, DataFrame)
    - File operations (save/load various formats)
    - Mathematical calculations
    """

    # ==================== Time Operations ====================

    @staticmethod
    def convert_time(
        time_value: Union[datetime, int, float, str],
        output_format: str = "datetime"
    ) -> Union[datetime, int, float, str]:
        """
        Convert time between different formats.

        Args:
            time_value: Input time (datetime, timestamp, or ISO string)
            output_format: Desired output format:
                - 'datetime': Python datetime object
                - 'timestamp': Unix timestamp (int)
                - 'iso': ISO format string
                - 'mt5': MT5 timestamp format

        Returns:
            Converted time in requested format

        Raises:
            ValueError: If time_value format is not recognized or conversion fails
        """
        logger.debug(f"Converting time: {time_value} to format: {output_format}")

        try:
            # Convert input to datetime first
            if isinstance(time_value, datetime):
                dt = time_value
            elif isinstance(time_value, (int, float)):
                # Assume Unix timestamp
                dt = datetime.fromtimestamp(time_value, tz=timezone.utc)
            elif isinstance(time_value, str):
                # Try to parse ISO format
                dt = datetime.fromisoformat(time_value.replace('Z', '+00:00'))
            else:
                raise ValueError(f"Unsupported time value type: {type(time_value)}")

            # Convert to requested format
            if output_format == "datetime":
                return dt
            elif output_format == "timestamp":
                return int(dt.timestamp())
            elif output_format == "iso":
                return dt.isoformat()
            elif output_format == "mt5":
                return int(dt.timestamp())
            else:
                raise ValueError(f"Unsupported output format: {output_format}")

        except Exception as e:
            logger.error(f"Error converting time: {e}")
            raise ValueError(f"Failed to convert time: {e}")

    @staticmethod
    def get_time(
        time_type: str = "now",
        timezone_offset: int = 0,
        format_str: Optional[str] = None
    ) -> Union[datetime, str]:
        """
        Get current or specific time.

        Args:
            time_type: Type of time to get:
                - 'now': Current UTC time
                - 'local': Current local time
                - 'mt5': MT5 server time (if connected)
            timezone_offset: Hours offset from UTC (default: 0)
            format_str: Optional strftime format string

        Returns:
            datetime object or formatted string if format_str provided

        Raises:
            ValueError: If time_type is not recognized
        """
        logger.debug(f"Getting time: type={time_type}, offset={timezone_offset}")

        try:
            if time_type == "now":
                dt = datetime.now(timezone.utc)
            elif time_type == "local":
                dt = datetime.now()
            elif time_type == "mt5":
                # Get MT5 server time if available
                if mt5.initialize():
                    terminal_info = mt5.terminal_info()
                    if terminal_info:
                        # MT5 doesn't directly expose server time, use local
                        dt = datetime.now(timezone.utc)
                    else:
                        dt = datetime.now(timezone.utc)
                else:
                    logger.warning("MT5 not initialized, using UTC time")
                    dt = datetime.now(timezone.utc)
            else:
                raise ValueError(f"Unsupported time_type: {time_type}")

            # Apply timezone offset
            if timezone_offset != 0:
                dt = dt + timedelta(hours=timezone_offset)

            # Format if requested
            if format_str:
                return dt.strftime(format_str)

            return dt

        except Exception as e:
            logger.error(f"Error getting time: {e}")
            raise ValueError(f"Failed to get time: {e}")

    # ==================== Price Operations ====================

    @staticmethod
    def convert_price(
        price: Union[float, int],
        from_digits: int,
        to_digits: int
    ) -> float:
        """
        Convert price between different digit precisions.

        Args:
            price: Price value to convert
            from_digits: Current number of decimal digits
            to_digits: Target number of decimal digits

        Returns:
            Converted price value
        """
        logger.debug(f"Converting price {price} from {from_digits} to {to_digits} digits")

        if from_digits == to_digits:
            return float(price)

        # Convert to points and back
        multiplier = 10 ** (to_digits - from_digits)
        return float(price * multiplier)

    @staticmethod
    def format_price(
        price: Union[float, int],
        digits: int = 5,
        include_currency: bool = False,
        currency_symbol: str = ""
    ) -> str:
        """
        Format price for display.

        Args:
            price: Price value to format
            digits: Number of decimal places
            include_currency: Whether to include currency symbol
            currency_symbol: Currency symbol to use (e.g., '$', 'EUR')

        Returns:
            Formatted price string
        """
        formatted = f"{float(price):.{digits}f}"

        if include_currency and currency_symbol:
            return f"{currency_symbol}{formatted}"

        return formatted

    @staticmethod
    def round_price(
        price: Union[float, int],
        tick_size: float,
        direction: str = "nearest"
    ) -> float:
        """
        Round price to valid tick size.

        Args:
            price: Price to round
            tick_size: Minimum price increment
            direction: Rounding direction:
                - 'nearest': Round to nearest tick
                - 'up': Round up to next tick
                - 'down': Round down to previous tick

        Returns:
            Rounded price value

        Raises:
            ValueError: If direction is not recognized
        """
        logger.debug(f"Rounding price {price} to tick_size {tick_size}, direction: {direction}")

        if tick_size <= 0:
            raise ValueError("tick_size must be positive")

        if direction == "nearest":
            return round(price / tick_size) * tick_size
        elif direction == "up":
            import math
            return math.ceil(price / tick_size) * tick_size
        elif direction == "down":
            import math
            return math.floor(price / tick_size) * tick_size
        else:
            raise ValueError(f"Invalid direction: {direction}. Use 'nearest', 'up', or 'down'")

    # ==================== Volume Operations ====================

    @staticmethod
    def convert_volume(
        volume: Union[float, int],
        from_unit: str = "lots",
        to_unit: str = "units",
        contract_size: int = 100000
    ) -> float:
        """
        Convert volume between different units.

        Args:
            volume: Volume value to convert
            from_unit: Current unit ('lots', 'units', 'mini_lots', 'micro_lots')
            to_unit: Target unit ('lots', 'units', 'mini_lots', 'micro_lots')
            contract_size: Contract size for the symbol (default: 100000 for forex)

        Returns:
            Converted volume value

        Raises:
            ValueError: If unit is not recognized
        """
        logger.debug(f"Converting volume {volume} from {from_unit} to {to_unit}")

        # Define conversion factors (relative to lots)
        units_map = {
            "lots": 1.0,
            "mini_lots": 10.0,
            "micro_lots": 100.0,
            "units": contract_size
        }

        if from_unit not in units_map:
            raise ValueError(f"Invalid from_unit: {from_unit}")
        if to_unit not in units_map:
            raise ValueError(f"Invalid to_unit: {to_unit}")

        # Convert to lots first, then to target unit
        volume_in_lots = volume / units_map[from_unit]
        result = volume_in_lots * units_map[to_unit]

        return float(result)

    @staticmethod
    def round_volume(
        volume: Union[float, int],
        volume_step: float,
        direction: str = "nearest"
    ) -> float:
        """
        Round volume to valid step size.

        Args:
            volume: Volume to round
            volume_step: Minimum volume increment
            direction: Rounding direction ('nearest', 'up', 'down')

        Returns:
            Rounded volume value

        Raises:
            ValueError: If direction is not recognized
        """
        logger.debug(f"Rounding volume {volume} to step {volume_step}, direction: {direction}")

        if volume_step <= 0:
            raise ValueError("volume_step must be positive")

        if direction == "nearest":
            return round(volume / volume_step) * volume_step
        elif direction == "up":
            import math
            return math.ceil(volume / volume_step) * volume_step
        elif direction == "down":
            import math
            return math.floor(volume / volume_step) * volume_step
        else:
            raise ValueError(f"Invalid direction: {direction}. Use 'nearest', 'up', or 'down'")

    # ==================== Type Conversions ====================

    @staticmethod
    def convert_type(
        value: Any,
        target_type: str
    ) -> Any:
        """
        Convert value to target type.

        Args:
            value: Value to convert
            target_type: Target type name:
                - 'int', 'float', 'str', 'bool'
                - 'list', 'dict', 'tuple'
                - 'datetime'

        Returns:
            Converted value

        Raises:
            ValueError: If conversion fails or type is not supported
        """
        logger.debug(f"Converting {value} to type {target_type}")

        try:
            if target_type == "int":
                return int(value)
            elif target_type == "float":
                return float(value)
            elif target_type == "str":
                return str(value)
            elif target_type == "bool":
                if isinstance(value, str):
                    return value.lower() in ('true', '1', 'yes', 'on')
                return bool(value)
            elif target_type == "list":
                if isinstance(value, (list, tuple, set)):
                    return list(value)
                return [value]
            elif target_type == "dict":
                if isinstance(value, dict):
                    return value
                raise ValueError(f"Cannot convert {type(value)} to dict")
            elif target_type == "tuple":
                if isinstance(value, (list, tuple, set)):
                    return tuple(value)
                return (value,)
            elif target_type == "datetime":
                return MT5Utils.convert_time(value, "datetime")
            else:
                raise ValueError(f"Unsupported target type: {target_type}")

        except Exception as e:
            logger.error(f"Error converting type: {e}")
            raise ValueError(f"Failed to convert to {target_type}: {e}")

    # ==================== Data Formatting ====================

    @staticmethod
    def to_dict(
        data: Any,
        exclude_none: bool = False,
        exclude_private: bool = True
    ) -> Dict[str, Any]:
        """
        Convert data to dictionary format.

        Args:
            data: Data to convert (MT5 named tuple, object, etc.)
            exclude_none: Whether to exclude None values
            exclude_private: Whether to exclude private attributes (starting with _)

        Returns:
            Dictionary representation of data
        """
        logger.debug(f"Converting to dict: {type(data)}")

        result = {}

        try:
            # Handle MT5 named tuples
            if hasattr(data, '_asdict'):
                result = data._asdict()
            # Handle regular objects with __dict__
            elif hasattr(data, '__dict__'):
                result = data.__dict__.copy()
            # Handle dictionaries
            elif isinstance(data, dict):
                result = data.copy()
            # Handle iterables
            elif isinstance(data, (list, tuple)):
                return {'items': list(data)}
            else:
                # Try to convert to string representation
                return {'value': str(data)}

            # Filter None values if requested
            if exclude_none:
                result = {k: v for k, v in result.items() if v is not None}

            # Filter private attributes if requested
            if exclude_private:
                result = {k: v for k, v in result.items() if not k.startswith('_')}

            return result

        except Exception as e:
            logger.error(f"Error converting to dict: {e}")
            raise ValueError(f"Failed to convert to dict: {e}")

    @staticmethod
    def to_dataframe(
        data: Union[List, tuple, Dict],
        columns: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Convert data to pandas DataFrame.

        Args:
            data: Data to convert (list of dicts, list of tuples, etc.)
            columns: Optional column names

        Returns:
            pandas DataFrame

        Raises:
            ValueError: If data cannot be converted to DataFrame
        """
        logger.debug(f"Converting to DataFrame: {type(data)}")

        try:
            # Handle list of MT5 named tuples
            if isinstance(data, (list, tuple)) and len(data) > 0:
                if hasattr(data[0], '_asdict'):
                    # Convert named tuples to dicts
                    data = [item._asdict() for item in data]

            # Create DataFrame
            df = pd.DataFrame(data, columns=columns)

            logger.debug(f"Created DataFrame with shape: {df.shape}")
            return df

        except Exception as e:
            logger.error(f"Error converting to DataFrame: {e}")
            raise ValueError(f"Failed to convert to DataFrame: {e}")

    # ==================== File Operations ====================

    @staticmethod
    def save(
        data: Any,
        filepath: Union[str, Path],
        format: str = "json",
        **kwargs
    ) -> bool:
        """
        Save data to file.

        Args:
            data: Data to save
            filepath: Path to save file
            format: File format ('json', 'csv', 'pickle')
            **kwargs: Additional arguments for specific formats

        Returns:
            True if successful

        Raises:
            ValueError: If format is not supported or save fails
        """
        logger.info(f"Saving data to {filepath} in {format} format")

        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        try:
            if format == "json":
                with open(filepath, 'w') as f:
                    json.dump(data, f, indent=kwargs.get('indent', 2), default=str)

            elif format == "csv":
                if isinstance(data, pd.DataFrame):
                    data.to_csv(filepath, index=kwargs.get('index', False))
                elif isinstance(data, (list, tuple)):
                    with open(filepath, 'w', newline='') as f:
                        if len(data) > 0 and isinstance(data[0], dict):
                            writer = csv.DictWriter(f, fieldnames=data[0].keys())
                            writer.writeheader()
                            writer.writerows(data)
                        else:
                            writer = csv.writer(f)
                            writer.writerows(data)
                else:
                    raise ValueError("CSV format requires DataFrame or list of dicts")

            elif format == "pickle":
                with open(filepath, 'wb') as f:
                    pickle.dump(data, f)

            else:
                raise ValueError(f"Unsupported format: {format}")

            logger.info(f"Successfully saved data to {filepath}")
            return True

        except Exception as e:
            logger.error(f"Error saving file: {e}")
            raise ValueError(f"Failed to save file: {e}")

    @staticmethod
    def load(
        filepath: Union[str, Path],
        format: str = "json",
        **kwargs
    ) -> Any:
        """
        Load data from file.

        Args:
            filepath: Path to load file from
            format: File format ('json', 'csv', 'pickle')
            **kwargs: Additional arguments for specific formats

        Returns:
            Loaded data

        Raises:
            ValueError: If format is not supported or load fails
            FileNotFoundError: If file doesn't exist
        """
        logger.info(f"Loading data from {filepath} in {format} format")

        filepath = Path(filepath)

        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        try:
            if format == "json":
                with open(filepath, 'r') as f:
                    data = json.load(f)

            elif format == "csv":
                data = pd.read_csv(filepath, **kwargs)

            elif format == "pickle":
                with open(filepath, 'rb') as f:
                    data = pickle.load(f)

            else:
                raise ValueError(f"Unsupported format: {format}")

            logger.info(f"Successfully loaded data from {filepath}")
            return data

        except Exception as e:
            logger.error(f"Error loading file: {e}")
            raise ValueError(f"Failed to load file: {e}")

    # ==================== Calculations ====================

    @staticmethod
    def calculate(
        operation: str,
        *args,
        **kwargs
    ) -> Union[float, int, Any]:
        """
        Perform various calculations.

        Args:
            operation: Type of calculation:
                - 'pip_value': Calculate pip value
                - 'profit': Calculate profit/loss
                - 'margin': Calculate required margin
                - 'percent': Calculate percentage
                - 'percent_change': Calculate percentage change
            *args: Positional arguments for calculation
            **kwargs: Keyword arguments for calculation

        Returns:
            Calculation result

        Raises:
            ValueError: If operation is not supported
        """
        logger.debug(f"Performing calculation: {operation}")

        try:
            if operation == "pip_value":
                # Args: symbol_info, volume
                return MT5Utils._calculate_pip_value(*args, **kwargs)

            elif operation == "profit":
                # Args: entry_price, exit_price, volume, contract_size
                return MT5Utils._calculate_profit(*args, **kwargs)

            elif operation == "margin":
                # Args: volume, price, leverage, contract_size
                return MT5Utils._calculate_margin(*args, **kwargs)

            elif operation == "percent":
                # Args: value, total
                value = args[0] if args else kwargs.get('value')
                total = args[1] if len(args) > 1 else kwargs.get('total')
                if total == 0:
                    return 0.0
                return (value / total) * 100

            elif operation == "percent_change":
                # Args: old_value, new_value
                old = args[0] if args else kwargs.get('old_value')
                new = args[1] if len(args) > 1 else kwargs.get('new_value')
                if old == 0:
                    return 0.0
                return ((new - old) / old) * 100

            else:
                raise ValueError(f"Unsupported operation: {operation}")

        except Exception as e:
            logger.error(f"Error in calculation: {e}")
            raise ValueError(f"Calculation failed: {e}")

    # ==================== Private Helper Methods ====================

    @staticmethod
    def _calculate_pip_value(
        symbol_info: Any,
        volume: float
    ) -> float:
        """Calculate pip value for a position."""
        point = symbol_info.point
        contract_size = symbol_info.trade_contract_size
        return point * contract_size * volume

    @staticmethod
    def _calculate_profit(
        entry_price: float,
        exit_price: float,
        volume: float,
        contract_size: int = 100000,
        direction: str = "buy"
    ) -> float:
        """Calculate profit/loss for a trade."""
        price_diff = exit_price - entry_price
        if direction == "sell":
            price_diff = -price_diff
        return price_diff * volume * contract_size

    @staticmethod
    def _calculate_margin(
        volume: float,
        price: float,
        leverage: int = 100,
        contract_size: int = 100000
    ) -> float:
        """Calculate required margin for a position."""
        return (volume * contract_size * price) / leverage


# Export the class
__all__ = ['MT5Utils']
