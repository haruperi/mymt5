from mylogger import logger
"""
MT5Risk - Risk management and position sizing for MetaTrader 5.

This module provides comprehensive risk management functionality including
position sizing, risk calculations, limit management, and portfolio risk analysis.
"""

import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Union, Dict, List, Any, Tuple
from pathlib import Path
import json


class MT5Risk:
    """
    Risk management and position sizing class.

    Provides methods for:
    - Position sizing calculations
    - Risk metric calculations
    - Risk limit management
    - Risk validation
    - Portfolio risk analysis
    """

    def __init__(self, client=None, account_info=None):
        """
        Initialize MT5Risk instance.

        Args:
            client: MT5Client instance for connection management (optional)
            account_info: MT5Account instance for account information (optional)
        """
        self.client = client
        self.account_info = account_info

        # Risk limits (defaults)
        self._limits = {
            'max_risk_per_trade': 2.0,  # Percent
            'max_daily_loss': 5.0,  # Percent
            'max_positions': 10,
            'max_symbol_positions': 3,
            'max_total_exposure': 20.0,  # Percent
        }

        logger.info("MT5Risk initialized")

    def calculate_size(
        self,
        symbol: str,
        method: str = 'percent',
        risk_amount: Optional[float] = None,
        risk_percent: Optional[float] = None,
        stop_loss_points: Optional[float] = None,
        entry_price: Optional[float] = None,
        stop_loss_price: Optional[float] = None
    ) -> Optional[float]:
        """
        Calculate position size based on risk parameters.

        Args:
            symbol: Trading symbol
            method: Sizing method ('percent', 'amount', 'ratio')
            risk_amount: Risk amount in account currency
            risk_percent: Risk as percentage of balance
            stop_loss_points: Stop loss distance in points
            entry_price: Entry price
            stop_loss_price: Stop loss price

        Returns:
            Calculated lot size or None on error

        Examples:
            >>> # Risk 2% of balance with 50 point SL
            >>> size = mt5_risk.calculate_size("EURUSD", method='percent',
            ...                                risk_percent=2.0, stop_loss_points=50)
            >>> # Risk $100 with SL at 1.0950
            >>> size = mt5_risk.calculate_size("EURUSD", method='amount',
            ...                                risk_amount=100, entry_price=1.1000,
            ...                                stop_loss_price=1.0950)
        """
        try:
            if method == 'percent':
                return self._calculate_position_size_percent(
                    symbol, risk_percent, stop_loss_points, entry_price, stop_loss_price
                )
            elif method == 'amount':
                return self._calculate_position_size_amount(
                    symbol, risk_amount, stop_loss_points, entry_price, stop_loss_price
                )
            elif method == 'ratio':
                # Fixed ratio based on balance
                account_info = mt5.account_info()
                if account_info is None:
                    return None

                symbol_info = mt5.symbol_info(symbol)
                if symbol_info is None:
                    return None

                # Simple ratio: 1 lot per $10,000
                ratio = risk_amount if risk_amount else 10000
                size = account_info.balance / ratio
                return round(size / symbol_info.volume_step) * symbol_info.volume_step
            else:
                logger.error(f"Unknown method: {method}")
                return None

        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return None

    def _calculate_position_size_percent(
        self,
        symbol: str,
        risk_percent: float,
        stop_loss_points: Optional[float] = None,
        entry_price: Optional[float] = None,
        stop_loss_price: Optional[float] = None
    ) -> Optional[float]:
        """Calculate position size based on percent risk."""
        try:
            # Get account info
            account_info = mt5.account_info()
            if account_info is None:
                logger.error("Failed to get account info")
                return None

            # Get symbol info
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                logger.error(f"Failed to get symbol info for {symbol}")
                return None

            # Calculate risk amount
            risk_amount = account_info.balance * (risk_percent / 100)

            # Calculate SL distance
            if stop_loss_points:
                sl_distance = stop_loss_points * symbol_info.point
            elif entry_price and stop_loss_price:
                sl_distance = abs(entry_price - stop_loss_price)
            else:
                logger.error("Must provide stop_loss_points or entry/sl prices")
                return None

            # Calculate position size
            # Risk = Volume * SL_Distance * ContractSize * PointValue
            tick_value = symbol_info.trade_tick_value
            tick_size = symbol_info.trade_tick_size

            if tick_size == 0:
                logger.error("Invalid tick size")
                return None

            point_value = (tick_value / tick_size) * symbol_info.point

            if point_value == 0:
                logger.error("Invalid point value")
                return None

            volume = risk_amount / (sl_distance / symbol_info.point * point_value)

            # Round to valid volume step
            volume = round(volume / symbol_info.volume_step) * symbol_info.volume_step

            # Apply volume limits
            volume = max(symbol_info.volume_min, min(volume, symbol_info.volume_max))

            logger.info(f"Calculated position size: {volume} lots (risk: {risk_percent}%)")
            return volume

        except Exception as e:
            logger.error(f"Error calculating position size (percent): {e}")
            return None

    def _calculate_position_size_amount(
        self,
        symbol: str,
        risk_amount: float,
        stop_loss_points: Optional[float] = None,
        entry_price: Optional[float] = None,
        stop_loss_price: Optional[float] = None
    ) -> Optional[float]:
        """Calculate position size based on fixed risk amount."""
        try:
            # Get symbol info
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                logger.error(f"Failed to get symbol info for {symbol}")
                return None

            # Calculate SL distance
            if stop_loss_points:
                sl_distance = stop_loss_points * symbol_info.point
            elif entry_price and stop_loss_price:
                sl_distance = abs(entry_price - stop_loss_price)
            else:
                logger.error("Must provide stop_loss_points or entry/sl prices")
                return None

            # Calculate position size
            tick_value = symbol_info.trade_tick_value
            tick_size = symbol_info.trade_tick_size

            if tick_size == 0:
                return None

            point_value = (tick_value / tick_size) * symbol_info.point

            if point_value == 0:
                return None

            volume = risk_amount / (sl_distance / symbol_info.point * point_value)

            # Round and apply limits
            volume = round(volume / symbol_info.volume_step) * symbol_info.volume_step
            volume = max(symbol_info.volume_min, min(volume, symbol_info.volume_max))

            logger.info(f"Calculated position size: {volume} lots (risk: ${risk_amount})")
            return volume

        except Exception as e:
            logger.error(f"Error calculating position size (amount): {e}")
            return None

    def calculate_risk(
        self,
        symbol: str,
        volume: float,
        entry_price: float,
        stop_loss_price: float,
        metric: str = 'amount'
    ) -> Union[float, Dict, None]:
        """
        Calculate risk metrics for a trade.

        Args:
            symbol: Trading symbol
            volume: Position volume
            entry_price: Entry price
            stop_loss_price: Stop loss price
            metric: Metric to calculate ('amount', 'percent', 'reward_ratio', 'all')

        Returns:
            Risk metric value or dict of all metrics

        Examples:
            >>> risk_amount = mt5_risk.calculate_risk("EURUSD", 0.1, 1.1000, 1.0950,
            ...                                       metric='amount')
            >>> all_metrics = mt5_risk.calculate_risk("EURUSD", 0.1, 1.1000, 1.0950,
            ...                                       metric='all')
        """
        try:
            if metric == 'amount':
                return self._calculate_risk_amount(symbol, volume, entry_price, stop_loss_price)
            elif metric == 'percent':
                return self._calculate_risk_percent(symbol, volume, entry_price, stop_loss_price)
            elif metric == 'reward_ratio':
                # Need take profit for this
                return None
            elif metric == 'all':
                return {
                    'risk_amount': self._calculate_risk_amount(symbol, volume, entry_price, stop_loss_price),
                    'risk_percent': self._calculate_risk_percent(symbol, volume, entry_price, stop_loss_price),
                    'position_value': self._calculate_position_value(symbol, volume, entry_price),
                }
            else:
                logger.error(f"Unknown metric: {metric}")
                return None

        except Exception as e:
            logger.error(f"Error calculating risk: {e}")
            return None

    def _calculate_risk_amount(
        self,
        symbol: str,
        volume: float,
        entry_price: float,
        stop_loss_price: float
    ) -> Optional[float]:
        """Calculate risk amount in account currency."""
        try:
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                return None

            # Calculate SL distance
            sl_distance = abs(entry_price - stop_loss_price)

            # Calculate risk
            tick_value = symbol_info.trade_tick_value
            tick_size = symbol_info.trade_tick_size

            if tick_size == 0:
                return None

            point_value = (tick_value / tick_size) * symbol_info.point
            risk_amount = volume * (sl_distance / symbol_info.point) * point_value

            return float(risk_amount)

        except Exception as e:
            logger.error(f"Error calculating risk amount: {e}")
            return None

    def _calculate_risk_percent(
        self,
        symbol: str,
        volume: float,
        entry_price: float,
        stop_loss_price: float
    ) -> Optional[float]:
        """Calculate risk as percentage of balance."""
        try:
            risk_amount = self._calculate_risk_amount(symbol, volume, entry_price, stop_loss_price)
            if risk_amount is None:
                return None

            account_info = mt5.account_info()
            if account_info is None:
                return None

            risk_percent = (risk_amount / account_info.balance) * 100
            return float(risk_percent)

        except Exception as e:
            logger.error(f"Error calculating risk percent: {e}")
            return None

    def _calculate_position_value(
        self,
        symbol: str,
        volume: float,
        price: float
    ) -> Optional[float]:
        """Calculate position value."""
        try:
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                return None

            # Position value = volume * contract_size * price
            contract_size = symbol_info.trade_contract_size
            value = volume * contract_size * price

            return float(value)

        except Exception as e:
            logger.error(f"Error calculating position value: {e}")
            return None

    def set_limit(self, limit_type: str, value: float):
        """
        Set risk limit.

        Args:
            limit_type: Type of limit ('max_risk_per_trade', 'max_daily_loss',
                       'max_positions', 'max_symbol_positions', 'max_total_exposure')
            value: Limit value

        Examples:
            >>> mt5_risk.set_limit('max_risk_per_trade', 1.0)  # 1% max risk
            >>> mt5_risk.set_limit('max_positions', 5)  # Max 5 positions
        """
        if limit_type in self._limits:
            self._limits[limit_type] = value
            logger.info(f"Set {limit_type} = {value}")
        else:
            logger.error(f"Unknown limit type: {limit_type}")

    def get_limit(self, limit_type: str) -> Optional[float]:
        """
        Get risk limit value.

        Args:
            limit_type: Type of limit

        Returns:
            Limit value or None

        Examples:
            >>> max_risk = mt5_risk.get_limit('max_risk_per_trade')
        """
        return self._limits.get(limit_type)

    def validate(self, trade_params: Dict) -> Tuple[bool, List[str]]:
        """
        Validate trade against risk limits.

        Args:
            trade_params: Trade parameters dict with keys:
                         symbol, volume, entry_price, stop_loss_price

        Returns:
            Tuple of (is_valid, list of violations)

        Examples:
            >>> valid, violations = mt5_risk.validate({
            ...     'symbol': 'EURUSD',
            ...     'volume': 0.1,
            ...     'entry_price': 1.1000,
            ...     'stop_loss_price': 1.0950
            ... })
        """
        violations = []

        try:
            # Check risk per trade
            risk_percent = self._calculate_risk_percent(
                trade_params['symbol'],
                trade_params['volume'],
                trade_params['entry_price'],
                trade_params['stop_loss_price']
            )

            if risk_percent and risk_percent > self._limits['max_risk_per_trade']:
                violations.append(f"Risk per trade ({risk_percent:.2f}%) exceeds limit ({self._limits['max_risk_per_trade']}%)")

            # Check position count
            positions = mt5.positions_total()
            if positions >= self._limits['max_positions']:
                violations.append(f"Position count ({positions}) at limit ({self._limits['max_positions']})")

            # Check symbol positions
            symbol_positions = len(mt5.positions_get(symbol=trade_params['symbol']) or [])
            if symbol_positions >= self._limits['max_symbol_positions']:
                violations.append(f"Symbol position count ({symbol_positions}) at limit ({self._limits['max_symbol_positions']})")

            # Check total exposure
            portfolio_risk = self.get_portfolio_risk('total_exposure')
            if portfolio_risk and portfolio_risk > self._limits['max_total_exposure']:
                violations.append(f"Total exposure ({portfolio_risk:.2f}%) exceeds limit ({self._limits['max_total_exposure']}%)")

            is_valid = len(violations) == 0
            return is_valid, violations

        except Exception as e:
            logger.error(f"Error validating trade: {e}")
            return False, [str(e)]

    def check(self, check_type: str) -> bool:
        """
        Perform risk checks.

        Args:
            check_type: Type of check ('trade_allowed', 'margin_available',
                       'risk_within_limits', 'stop_loss_valid', 'take_profit_valid')

        Returns:
            True if check passes, False otherwise

        Examples:
            >>> if mt5_risk.check('trade_allowed'):
            ...     # Execute trade
        """
        try:
            if check_type == 'trade_allowed':
                account_info = mt5.account_info()
                return account_info and account_info.trade_allowed

            elif check_type == 'margin_available':
                account_info = mt5.account_info()
                if account_info is None:
                    return False
                margin_level = account_info.margin_level if account_info.margin > 0 else float('inf')
                return margin_level > 100  # At least 100% margin level

            elif check_type == 'risk_within_limits':
                # Check if current positions are within limits
                positions = mt5.positions_total()
                return positions < self._limits['max_positions']

            else:
                logger.error(f"Unknown check type: {check_type}")
                return False

        except Exception as e:
            logger.error(f"Error performing check: {e}")
            return False

    def get_portfolio_risk(
        self,
        metric: str = 'all'
    ) -> Union[float, Dict, None]:
        """
        Calculate portfolio risk metrics.

        Args:
            metric: Metric to calculate ('total_exposure', 'total_risk',
                   'margin_usage', 'all')

        Returns:
            Risk metric value or dict of all metrics

        Examples:
            >>> exposure = mt5_risk.get_portfolio_risk('total_exposure')
            >>> all_metrics = mt5_risk.get_portfolio_risk('all')
        """
        try:
            if metric == 'total_exposure':
                return self._calculate_total_exposure()
            elif metric == 'total_risk':
                return self._calculate_total_risk()
            elif metric == 'margin_usage':
                return self._calculate_margin_usage()
            elif metric == 'all':
                return {
                    'total_exposure': self._calculate_total_exposure(),
                    'total_risk': self._calculate_total_risk(),
                    'margin_usage': self._calculate_margin_usage(),
                    'position_count': mt5.positions_total(),
                    'order_count': mt5.orders_total(),
                }
            else:
                logger.error(f"Unknown metric: {metric}")
                return None

        except Exception as e:
            logger.error(f"Error calculating portfolio risk: {e}")
            return None

    def _calculate_total_exposure(self) -> Optional[float]:
        """Calculate total portfolio exposure as percent of balance."""
        try:
            account_info = mt5.account_info()
            if account_info is None or account_info.balance == 0:
                return None

            positions = mt5.positions_get()
            if positions is None or len(positions) == 0:
                return 0.0

            total_value = 0.0
            for pos in positions:
                symbol_info = mt5.symbol_info(pos.symbol)
                if symbol_info:
                    pos_value = pos.volume * symbol_info.trade_contract_size * pos.price_open
                    total_value += pos_value

            exposure_percent = (total_value / account_info.balance) * 100
            return float(exposure_percent)

        except Exception as e:
            logger.error(f"Error calculating total exposure: {e}")
            return None

    def _calculate_total_risk(self) -> Optional[float]:
        """Calculate total risk across all positions."""
        try:
            positions = mt5.positions_get()
            if positions is None or len(positions) == 0:
                return 0.0

            total_risk = 0.0
            for pos in positions:
                if pos.sl > 0:
                    risk = self._calculate_risk_amount(
                        pos.symbol, pos.volume, pos.price_open, pos.sl
                    )
                    if risk:
                        total_risk += risk

            return float(total_risk)

        except Exception as e:
            logger.error(f"Error calculating total risk: {e}")
            return None

    def _calculate_margin_usage(self) -> Optional[float]:
        """Calculate margin usage percentage."""
        try:
            account_info = mt5.account_info()
            if account_info is None or account_info.equity == 0:
                return None

            if account_info.margin == 0:
                return 0.0

            margin_usage = (account_info.margin / account_info.equity) * 100
            return float(margin_usage)

        except Exception as e:
            logger.error(f"Error calculating margin usage: {e}")
            return None

    def get_summary(self) -> Dict[str, Any]:
        """
        Get risk management summary.

        Returns:
            Dict with risk summary

        Examples:
            >>> summary = mt5_risk.get_summary()
        """
        try:
            summary = {
                'limits': self._limits.copy(),
                'portfolio': self.get_portfolio_risk('all'),
                'checks': {
                    'trade_allowed': self.check('trade_allowed'),
                    'margin_available': self.check('margin_available'),
                    'risk_within_limits': self.check('risk_within_limits'),
                }
            }

            return summary

        except Exception as e:
            logger.error(f"Error getting summary: {e}")
            return {}

    def export_limits(self, filepath: Union[str, Path]) -> bool:
        """
        Export risk limits to JSON file.

        Args:
            filepath: Output file path

        Returns:
            True if successful, False otherwise

        Examples:
            >>> mt5_risk.export_limits('risk_limits.json')
        """
        try:
            filepath = Path(filepath)
            filepath.parent.mkdir(parents=True, exist_ok=True)

            data = {
                'limits': self._limits,
                'timestamp': datetime.now().isoformat(),
            }

            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)

            logger.info(f"Exported risk limits to {filepath}")
            return True

        except Exception as e:
            logger.error(f"Error exporting limits: {e}")
            return False
