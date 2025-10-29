"""
Unit tests for MT5 Trading System Utilities

Tests all utility methods including time operations, price/volume conversions,
data formatting, file operations, and calculations.
"""

import pytest
import tempfile
import json
import pickle
from datetime import datetime, timezone, timedelta
from pathlib import Path
import pandas as pd
from mymt5.utils import MT5Utils


class TestTimeOperations:
    """Test suite for time operation methods."""

    def test_convert_time_datetime_to_timestamp(self):
        """Test converting datetime to timestamp."""
        dt = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        timestamp = MT5Utils.convert_time(dt, "timestamp")
        assert isinstance(timestamp, int)
        assert timestamp == int(dt.timestamp())

    def test_convert_time_timestamp_to_datetime(self):
        """Test converting timestamp to datetime."""
        timestamp = 1704110400  # 2024-01-01 12:00:00 UTC
        dt = MT5Utils.convert_time(timestamp, "datetime")
        assert isinstance(dt, datetime)
        assert dt.year == 2024

    def test_convert_time_datetime_to_iso(self):
        """Test converting datetime to ISO format."""
        dt = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        iso_str = MT5Utils.convert_time(dt, "iso")
        assert isinstance(iso_str, str)
        assert "2024-01-01" in iso_str

    def test_convert_time_iso_to_datetime(self):
        """Test converting ISO string to datetime."""
        iso_str = "2024-01-01T12:00:00+00:00"
        dt = MT5Utils.convert_time(iso_str, "datetime")
        assert isinstance(dt, datetime)
        assert dt.year == 2024

    def test_convert_time_invalid_format(self):
        """Test that invalid format raises ValueError."""
        dt = datetime.now()
        with pytest.raises(ValueError, match="Unsupported output format"):
            MT5Utils.convert_time(dt, "invalid_format")

    def test_get_time_now(self):
        """Test getting current UTC time."""
        now = MT5Utils.get_time("now")
        assert isinstance(now, datetime)
        assert now.tzinfo == timezone.utc

    def test_get_time_local(self):
        """Test getting local time."""
        local = MT5Utils.get_time("local")
        assert isinstance(local, datetime)

    def test_get_time_with_offset(self):
        """Test getting time with timezone offset."""
        base_time = MT5Utils.get_time("now", timezone_offset=0)
        offset_time = MT5Utils.get_time("now", timezone_offset=2)
        diff = (offset_time - base_time).total_seconds()
        assert abs(diff - 7200) < 10  # 2 hours with small tolerance

    def test_get_time_with_format(self):
        """Test getting formatted time string."""
        time_str = MT5Utils.get_time("now", format_str="%Y-%m-%d")
        assert isinstance(time_str, str)
        assert len(time_str) == 10  # YYYY-MM-DD format


class TestPriceOperations:
    """Test suite for price operation methods."""

    def test_convert_price_increase_digits(self):
        """Test converting price to higher precision."""
        price = 1.12345
        result = MT5Utils.convert_price(price, from_digits=5, to_digits=3)
        assert result == 1.12345 * 0.01

    def test_convert_price_decrease_digits(self):
        """Test converting price to lower precision."""
        price = 1.12345
        result = MT5Utils.convert_price(price, from_digits=3, to_digits=5)
        assert result == 1.12345 * 100

    def test_convert_price_same_digits(self):
        """Test converting price with same digits."""
        price = 1.12345
        result = MT5Utils.convert_price(price, from_digits=5, to_digits=5)
        assert result == price

    def test_format_price_basic(self):
        """Test basic price formatting."""
        price = 1.123456789
        formatted = MT5Utils.format_price(price, digits=5)
        assert formatted == "1.12346"

    def test_format_price_with_currency(self):
        """Test price formatting with currency symbol."""
        price = 1.12345
        formatted = MT5Utils.format_price(price, digits=2, include_currency=True, currency_symbol="$")
        assert formatted == "$1.12"

    def test_round_price_nearest(self):
        """Test rounding price to nearest tick."""
        price = 1.12347
        rounded = MT5Utils.round_price(price, tick_size=0.00005, direction="nearest")
        assert rounded == 1.12345

    def test_round_price_up(self):
        """Test rounding price up."""
        price = 1.12341
        rounded = MT5Utils.round_price(price, tick_size=0.00005, direction="up")
        assert rounded == 1.12345

    def test_round_price_down(self):
        """Test rounding price down."""
        price = 1.12349
        rounded = MT5Utils.round_price(price, tick_size=0.00005, direction="down")
        assert rounded == 1.12345

    def test_round_price_invalid_direction(self):
        """Test that invalid direction raises ValueError."""
        with pytest.raises(ValueError, match="Invalid direction"):
            MT5Utils.round_price(1.12345, tick_size=0.00001, direction="invalid")

    def test_round_price_invalid_tick_size(self):
        """Test that invalid tick size raises ValueError."""
        with pytest.raises(ValueError, match="tick_size must be positive"):
            MT5Utils.round_price(1.12345, tick_size=0, direction="nearest")


class TestVolumeOperations:
    """Test suite for volume operation methods."""

    def test_convert_volume_lots_to_units(self):
        """Test converting lots to units."""
        volume = 1.0
        units = MT5Utils.convert_volume(volume, from_unit="lots", to_unit="units", contract_size=100000)
        assert units == 100000.0

    def test_convert_volume_mini_lots_to_lots(self):
        """Test converting mini lots to lots."""
        volume = 10.0
        lots = MT5Utils.convert_volume(volume, from_unit="mini_lots", to_unit="lots")
        assert lots == 1.0

    def test_convert_volume_micro_lots_to_lots(self):
        """Test converting micro lots to lots."""
        volume = 100.0
        lots = MT5Utils.convert_volume(volume, from_unit="micro_lots", to_unit="lots")
        assert lots == 1.0

    def test_convert_volume_same_unit(self):
        """Test converting volume with same unit."""
        volume = 1.5
        result = MT5Utils.convert_volume(volume, from_unit="lots", to_unit="lots")
        assert result == 1.5

    def test_convert_volume_invalid_unit(self):
        """Test that invalid unit raises ValueError."""
        with pytest.raises(ValueError, match="Invalid from_unit"):
            MT5Utils.convert_volume(1.0, from_unit="invalid", to_unit="lots")

    def test_round_volume_nearest(self):
        """Test rounding volume to nearest step."""
        volume = 1.07
        rounded = MT5Utils.round_volume(volume, volume_step=0.01, direction="nearest")
        assert rounded == 1.07

    def test_round_volume_up(self):
        """Test rounding volume up."""
        volume = 1.01
        rounded = MT5Utils.round_volume(volume, volume_step=0.1, direction="up")
        assert rounded == 1.1

    def test_round_volume_down(self):
        """Test rounding volume down."""
        volume = 1.09
        rounded = MT5Utils.round_volume(volume, volume_step=0.1, direction="down")
        assert rounded == 1.0

    def test_round_volume_invalid_step(self):
        """Test that invalid volume step raises ValueError."""
        with pytest.raises(ValueError, match="volume_step must be positive"):
            MT5Utils.round_volume(1.0, volume_step=-0.01, direction="nearest")


class TestTypeConversions:
    """Test suite for type conversion methods."""

    def test_convert_type_to_int(self):
        """Test converting to int."""
        assert MT5Utils.convert_type("123", "int") == 123
        assert MT5Utils.convert_type(123.7, "int") == 123

    def test_convert_type_to_float(self):
        """Test converting to float."""
        assert MT5Utils.convert_type("123.45", "float") == 123.45
        assert MT5Utils.convert_type(123, "float") == 123.0

    def test_convert_type_to_str(self):
        """Test converting to string."""
        assert MT5Utils.convert_type(123, "str") == "123"
        assert MT5Utils.convert_type(123.45, "str") == "123.45"

    def test_convert_type_to_bool(self):
        """Test converting to bool."""
        assert MT5Utils.convert_type("true", "bool") is True
        assert MT5Utils.convert_type("false", "bool") is False
        assert MT5Utils.convert_type(1, "bool") is True
        assert MT5Utils.convert_type(0, "bool") is False

    def test_convert_type_to_list(self):
        """Test converting to list."""
        assert MT5Utils.convert_type((1, 2, 3), "list") == [1, 2, 3]
        assert MT5Utils.convert_type({1, 2, 3}, "list") == [1, 2, 3]
        assert MT5Utils.convert_type(1, "list") == [1]

    def test_convert_type_to_tuple(self):
        """Test converting to tuple."""
        assert MT5Utils.convert_type([1, 2, 3], "tuple") == (1, 2, 3)
        assert MT5Utils.convert_type(1, "tuple") == (1,)

    def test_convert_type_invalid_type(self):
        """Test that invalid type raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported target type"):
            MT5Utils.convert_type(123, "invalid_type")


class TestDataFormatting:
    """Test suite for data formatting methods."""

    def test_to_dict_from_dict(self):
        """Test converting dict to dict."""
        data = {"key": "value", "num": 123}
        result = MT5Utils.to_dict(data)
        assert result == data
        assert result is not data  # Should be a copy

    def test_to_dict_exclude_none(self):
        """Test excluding None values."""
        data = {"key": "value", "none_key": None}
        result = MT5Utils.to_dict(data, exclude_none=True)
        assert "key" in result
        assert "none_key" not in result

    def test_to_dict_exclude_private(self):
        """Test excluding private attributes."""
        data = {"public": "value", "_private": "hidden"}
        result = MT5Utils.to_dict(data, exclude_private=True)
        assert "public" in result
        assert "_private" not in result

    def test_to_dict_from_list(self):
        """Test converting list to dict."""
        data = [1, 2, 3]
        result = MT5Utils.to_dict(data)
        assert "items" in result
        assert result["items"] == [1, 2, 3]

    def test_to_dataframe_from_list_of_dicts(self):
        """Test converting list of dicts to DataFrame."""
        data = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25}
        ]
        df = MT5Utils.to_dataframe(data)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert list(df.columns) == ["name", "age"]

    def test_to_dataframe_empty_list(self):
        """Test converting empty list to DataFrame."""
        df = MT5Utils.to_dataframe([])
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0

    def test_to_dataframe_with_columns(self):
        """Test converting data with explicit columns."""
        data = [[1, 2], [3, 4]]
        df = MT5Utils.to_dataframe(data, columns=["A", "B"])
        assert list(df.columns) == ["A", "B"]


class TestFileOperations:
    """Test suite for file operation methods."""

    def test_save_and_load_json(self):
        """Test saving and loading JSON files."""
        data = {"key": "value", "number": 123, "list": [1, 2, 3]}

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test.json"
            MT5Utils.save(data, filepath, format="json")
            assert filepath.exists()

            loaded = MT5Utils.load(filepath, format="json")
            assert loaded == data

    def test_save_and_load_pickle(self):
        """Test saving and loading pickle files."""
        data = {"key": "value", "complex": {"nested": "data"}}

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test.pkl"
            MT5Utils.save(data, filepath, format="pickle")
            assert filepath.exists()

            loaded = MT5Utils.load(filepath, format="pickle")
            assert loaded == data

    def test_save_and_load_csv_dataframe(self):
        """Test saving and loading CSV with DataFrame."""
        df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test.csv"
            MT5Utils.save(df, filepath, format="csv")
            assert filepath.exists()

            loaded = MT5Utils.load(filepath, format="csv")
            assert isinstance(loaded, pd.DataFrame)
            assert loaded.shape == df.shape

    def test_save_csv_list_of_dicts(self):
        """Test saving CSV from list of dicts."""
        data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test.csv"
            MT5Utils.save(data, filepath, format="csv")
            assert filepath.exists()

    def test_save_creates_directory(self):
        """Test that save creates parent directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "subdir" / "test.json"
            MT5Utils.save({"test": "data"}, filepath, format="json")
            assert filepath.exists()

    def test_load_nonexistent_file(self):
        """Test that loading nonexistent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            MT5Utils.load("nonexistent.json", format="json")

    def test_save_invalid_format(self):
        """Test that invalid format raises ValueError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test.txt"
            with pytest.raises(ValueError, match="Unsupported format"):
                MT5Utils.save({"test": "data"}, filepath, format="invalid")

    def test_load_invalid_format(self):
        """Test that invalid format raises ValueError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test.txt"
            filepath.touch()
            with pytest.raises(ValueError, match="Unsupported format"):
                MT5Utils.load(filepath, format="invalid")


class TestCalculations:
    """Test suite for calculation methods."""

    def test_calculate_percent(self):
        """Test percentage calculation."""
        result = MT5Utils.calculate("percent", 25, 100)
        assert result == 25.0

    def test_calculate_percent_zero_total(self):
        """Test percentage with zero total."""
        result = MT5Utils.calculate("percent", 10, 0)
        assert result == 0.0

    def test_calculate_percent_change(self):
        """Test percentage change calculation."""
        result = MT5Utils.calculate("percent_change", 100, 150)
        assert result == 50.0

    def test_calculate_percent_change_negative(self):
        """Test negative percentage change."""
        result = MT5Utils.calculate("percent_change", 100, 50)
        assert result == -50.0

    def test_calculate_percent_change_zero_old(self):
        """Test percentage change with zero old value."""
        result = MT5Utils.calculate("percent_change", 0, 100)
        assert result == 0.0

    def test_calculate_profit_buy(self):
        """Test profit calculation for buy position."""
        profit = MT5Utils.calculate(
            "profit",
            entry_price=1.1000,
            exit_price=1.1050,
            volume=1.0,
            contract_size=100000,
            direction="buy"
        )
        assert pytest.approx(profit, rel=1e-6) == 500.0

    def test_calculate_profit_sell(self):
        """Test profit calculation for sell position."""
        profit = MT5Utils.calculate(
            "profit",
            entry_price=1.1050,
            exit_price=1.1000,
            volume=1.0,
            contract_size=100000,
            direction="sell"
        )
        assert pytest.approx(profit, rel=1e-6) == 500.0

    def test_calculate_margin(self):
        """Test margin calculation."""
        margin = MT5Utils.calculate(
            "margin",
            volume=1.0,
            price=1.1000,
            leverage=100,
            contract_size=100000
        )
        assert pytest.approx(margin, rel=1e-6) == 1100.0

    def test_calculate_invalid_operation(self):
        """Test that invalid operation raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported operation"):
            MT5Utils.calculate("invalid_operation", 1, 2)


class TestIntegration:
    """Integration tests for combined utility operations."""

    def test_time_conversion_chain(self):
        """Test chaining time conversions."""
        # datetime -> timestamp -> datetime
        original = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        timestamp = MT5Utils.convert_time(original, "timestamp")
        converted = MT5Utils.convert_time(timestamp, "datetime")
        assert original.year == converted.year
        assert original.month == converted.month
        assert original.day == converted.day

    def test_price_and_volume_workflow(self):
        """Test realistic price and volume workflow."""
        # Format price
        price = 1.12345
        formatted = MT5Utils.format_price(price, digits=5)
        assert "1.12345" in formatted

        # Round price
        rounded = MT5Utils.round_price(price, tick_size=0.00005, direction="nearest")
        assert rounded == 1.12345

        # Convert and round volume
        volume_lots = 1.0
        volume_units = MT5Utils.convert_volume(volume_lots, "lots", "units")
        assert volume_units == 100000.0

    def test_data_save_load_workflow(self):
        """Test complete data save/load workflow."""
        # Create data
        data = {
            "timestamp": datetime.now().isoformat(),
            "price": 1.12345,
            "volume": 1.0
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            # Save as JSON
            json_path = Path(tmpdir) / "data.json"
            MT5Utils.save(data, json_path, format="json")

            # Load and verify
            loaded = MT5Utils.load(json_path, format="json")
            assert loaded["price"] == data["price"]
            assert loaded["volume"] == data["volume"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
