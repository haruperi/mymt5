from mylogger import logger
"""
MT5Trade - Order execution and position management for MetaTrader 5.

This module provides comprehensive functionality for executing trades,
managing orders and positions, and analyzing trading performance.
"""

import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Union, Dict, List, Any, Tuple
from pathlib import Path
import json

from .enums import OrderType
from .utils import MT5Utils


class MT5Trade:
    """
    Trading operations and position management class.

    Provides methods for:
    - Order execution (market, pending, limit, stop)
    - Order management (modify, cancel)
    - Position management (modify, close, reverse)
    - Position analytics and statistics
    - Trade validation
    """

    def __init__(self, client=None, symbol_info=None, account_info=None):
        """
        Initialize MT5Trade instance.

        Args:
            client: MT5Client instance for connection management (optional)
            symbol_info: MT5Symbol instance for symbol information (optional)
            account_info: MT5Account instance for account information (optional)
        """
        self.client = client
        self.symbol_info = symbol_info
        self.account_info = account_info

        logger.info("MT5Trade initialized")

    def execute(
        self,
        symbol: str,
        order_type: Union[str, OrderType, int],
        volume: float,
        price: Optional[float] = None,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
        deviation: int = 20,
        magic: int = 0,
        comment: str = "",
        type_time: int = mt5.ORDER_TIME_GTC,
        type_filling: int = mt5.ORDER_FILLING_IOC
    ) -> Optional[Dict]:
        """
        Execute a trading order.

        Args:
            symbol: Trading symbol
            order_type: Order type (BUY, SELL, BUY_LIMIT, etc.)
            volume: Trade volume in lots
            price: Order price (for pending orders)
            sl: Stop loss price
            tp: Take profit price
            deviation: Maximum price deviation in points
            magic: Magic number for order identification
            comment: Order comment
            type_time: Order lifetime type
            type_filling: Order filling type

        Returns:
            Dict with order result or None on error

        Examples:
            >>> # Market buy
            >>> result = mt5_trade.execute("EURUSD", "BUY", 0.1, sl=1.1250, tp=1.1350)
            >>> # Pending buy limit
            >>> result = mt5_trade.execute("EURUSD", "BUY_LIMIT", 0.1, price=1.1300)
        """
        try:
            # Build trade request
            request = self.build_request(
                symbol=symbol,
                order_type=order_type,
                volume=volume,
                price=price,
                sl=sl,
                tp=tp,
                deviation=deviation,
                magic=magic,
                comment=comment,
                type_time=type_time,
                type_filling=type_filling
            )

            if request is None:
                return None

            # Send order
            result = self._send_request(request)

            return result

        except Exception as e:
            logger.error(f"Error executing order: {e}")
            return None

    def buy(
        self,
        symbol: str,
        volume: float,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
        **kwargs
    ) -> Optional[Dict]:
        """
        Simplified market buy order.

        Args:
            symbol: Trading symbol
            volume: Trade volume in lots
            sl: Stop loss price
            tp: Take profit price
            **kwargs: Additional order parameters

        Returns:
            Dict with order result or None on error

        Examples:
            >>> result = mt5_trade.buy("EURUSD", 0.1, sl=1.1250, tp=1.1350)
        """
        return self.execute(symbol, OrderType.BUY, volume, sl=sl, tp=tp, **kwargs)

    def sell(
        self,
        symbol: str,
        volume: float,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
        **kwargs
    ) -> Optional[Dict]:
        """
        Simplified market sell order.

        Args:
            symbol: Trading symbol
            volume: Trade volume in lots
            sl: Stop loss price
            tp: Take profit price
            **kwargs: Additional order parameters

        Returns:
            Dict with order result or None on error

        Examples:
            >>> result = mt5_trade.sell("EURUSD", 0.1, sl=1.1350, tp=1.1250)
        """
        return self.execute(symbol, OrderType.SELL, volume, sl=sl, tp=tp, **kwargs)

    def build_request(
        self,
        symbol: str,
        order_type: Union[str, OrderType, int],
        volume: float,
        price: Optional[float] = None,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
        deviation: int = 20,
        magic: int = 0,
        comment: str = "",
        type_time: int = mt5.ORDER_TIME_GTC,
        type_filling: int = mt5.ORDER_FILLING_IOC
    ) -> Optional[Dict]:
        """
        Build trade request dictionary.

        Args:
            symbol: Trading symbol
            order_type: Order type
            volume: Trade volume
            price: Order price (for pending orders)
            sl: Stop loss
            tp: Take profit
            deviation: Price deviation
            magic: Magic number
            comment: Comment
            type_time: Time type
            type_filling: Filling type

        Returns:
            Trade request dict or None on error
        """
        try:
            # Convert order type to MT5 constant
            if isinstance(order_type, OrderType):
                mt5_order_type = order_type.value
            elif isinstance(order_type, str):
                mt5_order_type = OrderType[order_type.upper()].value
            else:
                mt5_order_type = order_type

            # Get current price if not provided (for market orders)
            if price is None:
                tick = mt5.symbol_info_tick(symbol)
                if tick is None:
                    logger.error(f"Failed to get tick for {symbol}")
                    return None

                # Use ask for buy, bid for sell
                if mt5_order_type in [mt5.ORDER_TYPE_BUY, mt5.ORDER_TYPE_BUY_LIMIT, mt5.ORDER_TYPE_BUY_STOP]:
                    price = tick.ask
                else:
                    price = tick.bid

            # Build request
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume,
                "type": mt5_order_type,
                "price": price,
                "deviation": deviation,
                "magic": magic,
                "comment": comment,
                "type_time": type_time,
                "type_filling": type_filling,
            }

            # Add SL/TP if provided
            if sl is not None:
                request["sl"] = sl
            if tp is not None:
                request["tp"] = tp

            # For pending orders, change action
            if mt5_order_type in [mt5.ORDER_TYPE_BUY_LIMIT, mt5.ORDER_TYPE_SELL_LIMIT,
                                  mt5.ORDER_TYPE_BUY_STOP, mt5.ORDER_TYPE_SELL_STOP,
                                  mt5.ORDER_TYPE_BUY_STOP_LIMIT, mt5.ORDER_TYPE_SELL_STOP_LIMIT]:
                request["action"] = mt5.TRADE_ACTION_PENDING

            logger.debug(f"Built trade request: {request}")
            return request

        except Exception as e:
            logger.error(f"Error building request: {e}")
            return None

    def _send_request(self, request: Dict) -> Optional[Dict]:
        """
        Internal method to send trade request to MT5.

        Args:
            request: Trade request dictionary

        Returns:
            Dict with result or None on error
        """
        try:
            result = mt5.order_send(request)

            if result is None:
                logger.error("order_send returned None")
                return None

            # Convert to dict
            result_dict = {
                'retcode': result.retcode,
                'deal': result.deal,
                'order': result.order,
                'volume': result.volume,
                'price': result.price,
                'bid': result.bid,
                'ask': result.ask,
                'comment': result.comment,
                'request_id': result.request_id,
                'retcode_external': result.retcode_external,
            }

            # Check result
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                logger.warning(f"Order failed: {result.comment} (retcode={result.retcode})")
            else:
                logger.info(f"Order executed successfully: deal={result.deal}, order={result.order}")

            return result_dict

        except Exception as e:
            logger.error(f"Error sending order: {e}")
            return None

    def get_orders(
        self,
        symbol: Optional[str] = None,
        ticket: Optional[int] = None,
        group: Optional[str] = None
    ) -> Optional[pd.DataFrame]:
        """
        Get open orders.

        Args:
            symbol: Filter by symbol (None for all)
            ticket: Get specific order by ticket
            group: Filter by symbol group

        Returns:
            DataFrame with orders or None

        Examples:
            >>> orders = mt5_trade.get_orders()
            >>> eurusd_orders = mt5_trade.get_orders(symbol="EURUSD")
        """
        try:
            if ticket:
                orders = mt5.orders_get(ticket=ticket)
            elif symbol:
                orders = mt5.orders_get(symbol=symbol)
            elif group:
                orders = mt5.orders_get(group=group)
            else:
                orders = mt5.orders_get()

            if orders is None or len(orders) == 0:
                logger.info("No open orders")
                return pd.DataFrame()

            df = pd.DataFrame(list(orders), columns=orders[0]._asdict().keys())
            df['time_setup'] = pd.to_datetime(df['time_setup'], unit='s')

            logger.info(f"Retrieved {len(df)} orders")
            return df

        except Exception as e:
            logger.error(f"Error getting orders: {e}")
            return None

    def modify_order(
        self,
        ticket: int,
        price: Optional[float] = None,
        sl: Optional[float] = None,
        tp: Optional[float] = None
    ) -> Optional[Dict]:
        """
        Modify an existing order.

        Args:
            ticket: Order ticket number
            price: New order price
            sl: New stop loss
            tp: New take profit

        Returns:
            Dict with result or None on error

        Examples:
            >>> result = mt5_trade.modify_order(12345, price=1.1300, sl=1.1250)
        """
        try:
            # Get order info
            order = mt5.orders_get(ticket=ticket)
            if order is None or len(order) == 0:
                logger.error(f"Order {ticket} not found")
                return None

            order = order[0]

            # Build modification request
            request = {
                "action": mt5.TRADE_ACTION_MODIFY,
                "order": ticket,
                "symbol": order.symbol,
                "type": order.type,
                "volume": order.volume_current,
            }

            # Add modified parameters
            if price is not None:
                request["price"] = price
            else:
                request["price"] = order.price_open

            if sl is not None:
                request["sl"] = sl
            elif hasattr(order, 'sl'):
                request["sl"] = order.sl

            if tp is not None:
                request["tp"] = tp
            elif hasattr(order, 'tp'):
                request["tp"] = order.tp

            # Send modification
            result = self._send_request(request)
            return result

        except Exception as e:
            logger.error(f"Error modifying order: {e}")
            return None

    def cancel_order(
        self,
        ticket: Optional[int] = None,
        symbol: Optional[str] = None,
        cancel_all: bool = False
    ) -> Union[Dict, List[Dict], None]:
        """
        Cancel order(s).

        Args:
            ticket: Specific order ticket to cancel
            symbol: Cancel all orders for symbol
            cancel_all: Cancel all orders

        Returns:
            Result dict or list of results, or None on error

        Examples:
            >>> mt5_trade.cancel_order(ticket=12345)
            >>> mt5_trade.cancel_order(symbol="EURUSD")
            >>> mt5_trade.cancel_order(cancel_all=True)
        """
        try:
            results = []

            if ticket:
                # Cancel specific order
                request = {
                    "action": mt5.TRADE_ACTION_REMOVE,
                    "order": ticket,
                }
                result = self._send_request(request)
                return result

            elif symbol or cancel_all:
                # Get orders to cancel
                orders = self.get_orders(symbol=symbol if symbol else None)

                if orders is None or len(orders) == 0:
                    logger.info("No orders to cancel")
                    return []

                # Cancel each order
                for _, order in orders.iterrows():
                    request = {
                        "action": mt5.TRADE_ACTION_REMOVE,
                        "order": order.ticket,
                    }
                    result = self._send_request(request)
                    if result:
                        results.append(result)

                logger.info(f"Cancelled {len(results)} orders")
                return results

            else:
                logger.error("Must specify ticket, symbol, or cancel_all")
                return None

        except Exception as e:
            logger.error(f"Error cancelling order: {e}")
            return None

    def get_positions(
        self,
        symbol: Optional[str] = None,
        ticket: Optional[int] = None,
        group: Optional[str] = None
    ) -> Optional[pd.DataFrame]:
        """
        Get open positions.

        Args:
            symbol: Filter by symbol
            ticket: Get specific position
            group: Filter by symbol group

        Returns:
            DataFrame with positions or None

        Examples:
            >>> positions = mt5_trade.get_positions()
            >>> eurusd_pos = mt5_trade.get_positions(symbol="EURUSD")
        """
        try:
            if ticket:
                positions = mt5.positions_get(ticket=ticket)
            elif symbol:
                positions = mt5.positions_get(symbol=symbol)
            elif group:
                positions = mt5.positions_get(group=group)
            else:
                positions = mt5.positions_get()

            if positions is None or len(positions) == 0:
                logger.info("No open positions")
                return pd.DataFrame()

            df = pd.DataFrame(list(positions), columns=positions[0]._asdict().keys())
            df['time'] = pd.to_datetime(df['time'], unit='s')

            logger.info(f"Retrieved {len(df)} positions")
            return df

        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return None

    def modify_position(
        self,
        symbol: str,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
        ticket: Optional[int] = None
    ) -> Optional[Dict]:
        """
        Modify position SL/TP.

        Args:
            symbol: Position symbol
            sl: New stop loss
            tp: New take profit
            ticket: Specific position ticket (optional)

        Returns:
            Dict with result or None on error

        Examples:
            >>> mt5_trade.modify_position("EURUSD", sl=1.1250, tp=1.1350)
        """
        try:
            # Get position
            if ticket:
                position = mt5.positions_get(ticket=ticket)
            else:
                position = mt5.positions_get(symbol=symbol)

            if position is None or len(position) == 0:
                logger.error(f"Position not found for {symbol}")
                return None

            position = position[0]

            # Build modification request
            request = {
                "action": mt5.TRADE_ACTION_SLTP,
                "symbol": symbol,
                "position": position.ticket,
            }

            if sl is not None:
                request["sl"] = sl
            else:
                request["sl"] = position.sl

            if tp is not None:
                request["tp"] = tp
            else:
                request["tp"] = position.tp

            # Send modification
            result = self._send_request(request)
            return result

        except Exception as e:
            logger.error(f"Error modifying position: {e}")
            return None

    def close_position(
        self,
        symbol: Optional[str] = None,
        ticket: Optional[int] = None,
        volume: Optional[float] = None,
        close_all: bool = False,
        deviation: int = 20
    ) -> Union[Dict, List[Dict], None]:
        """
        Close position(s).

        Args:
            symbol: Position symbol
            ticket: Specific position ticket
            volume: Partial close volume (None for full close)
            close_all: Close all positions
            deviation: Price deviation

        Returns:
            Result dict or list of results, or None on error

        Examples:
            >>> mt5_trade.close_position(symbol="EURUSD")
            >>> mt5_trade.close_position(ticket=12345, volume=0.05)  # Partial
            >>> mt5_trade.close_position(close_all=True)
        """
        try:
            results = []

            if ticket or symbol:
                # Close specific position
                if ticket:
                    position = mt5.positions_get(ticket=ticket)
                else:
                    position = mt5.positions_get(symbol=symbol)

                if position is None or len(position) == 0:
                    logger.error("Position not found")
                    return None

                position = position[0]

                # Determine close volume
                close_volume = volume if volume else position.volume

                # Determine close type (opposite of position type)
                if position.type == mt5.POSITION_TYPE_BUY:
                    close_type = mt5.ORDER_TYPE_SELL
                    price = mt5.symbol_info_tick(position.symbol).bid
                else:
                    close_type = mt5.ORDER_TYPE_BUY
                    price = mt5.symbol_info_tick(position.symbol).ask

                # Build close request
                request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": position.symbol,
                    "volume": close_volume,
                    "type": close_type,
                    "position": position.ticket,
                    "price": price,
                    "deviation": deviation,
                    "magic": position.magic,
                    "comment": "Close position",
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_IOC,
                }

                result = self._send_request(request)
                return result

            elif close_all:
                # Close all positions
                positions = self.get_positions()

                if positions is None or len(positions) == 0:
                    logger.info("No positions to close")
                    return []

                # Close each position
                for _, pos in positions.iterrows():
                    result = self.close_position(ticket=pos.ticket, deviation=deviation)
                    if result:
                        results.append(result)

                logger.info(f"Closed {len(results)} positions")
                return results

            else:
                logger.error("Must specify symbol, ticket, or close_all")
                return None

        except Exception as e:
            logger.error(f"Error closing position: {e}")
            return None

    def reverse_position(
        self,
        symbol: str,
        ticket: Optional[int] = None
    ) -> Optional[Dict]:
        """
        Reverse a position (close and open opposite).

        Args:
            symbol: Position symbol
            ticket: Specific position ticket

        Returns:
            Dict with result or None on error

        Examples:
            >>> mt5_trade.reverse_position("EURUSD")
        """
        try:
            # Get position
            if ticket:
                position = mt5.positions_get(ticket=ticket)
            else:
                position = mt5.positions_get(symbol=symbol)

            if position is None or len(position) == 0:
                logger.error("Position not found")
                return None

            position = position[0]

            # Close current position and open opposite
            if position.type == mt5.POSITION_TYPE_BUY:
                # Close buy, open sell
                result = self.sell(symbol, position.volume * 2)  # Double volume to reverse
            else:
                # Close sell, open buy
                result = self.buy(symbol, position.volume * 2)

            return result

        except Exception as e:
            logger.error(f"Error reversing position: {e}")
            return None

    def analyze_position(
        self,
        symbol: Optional[str] = None,
        ticket: Optional[int] = None,
        metric: str = 'all'
    ) -> Union[float, Dict, None]:
        """
        Analyze position metrics.

        Args:
            symbol: Position symbol
            ticket: Position ticket
            metric: Metric to calculate ('profit', 'profit_points', 'duration',
                   'current_price', 'entry_price', 'volume', 'all')

        Returns:
            Metric value or dict of all metrics

        Examples:
            >>> profit = mt5_trade.analyze_position("EURUSD", metric='profit')
            >>> all_metrics = mt5_trade.analyze_position("EURUSD", metric='all')
        """
        try:
            # Get position
            if ticket:
                position = mt5.positions_get(ticket=ticket)
            elif symbol:
                position = mt5.positions_get(symbol=symbol)
            else:
                logger.error("Must specify symbol or ticket")
                return None

            if position is None or len(position) == 0:
                logger.error("Position not found")
                return None

            position = position[0]

            # Calculate metrics
            if metric == 'profit':
                return float(position.profit)
            elif metric == 'profit_points':
                # Calculate profit in points
                tick = mt5.symbol_info_tick(position.symbol)
                if position.type == mt5.POSITION_TYPE_BUY:
                    return (tick.bid - position.price_open) * 10000  # For forex
                else:
                    return (position.price_open - tick.ask) * 10000
            elif metric == 'duration':
                duration = datetime.now() - datetime.fromtimestamp(position.time)
                return duration.total_seconds()
            elif metric == 'current_price':
                tick = mt5.symbol_info_tick(position.symbol)
                return tick.bid if position.type == mt5.POSITION_TYPE_BUY else tick.ask
            elif metric == 'entry_price':
                return float(position.price_open)
            elif metric == 'volume':
                return float(position.volume)
            elif metric == 'all':
                tick = mt5.symbol_info_tick(position.symbol)
                current_price = tick.bid if position.type == mt5.POSITION_TYPE_BUY else tick.ask

                return {
                    'ticket': position.ticket,
                    'symbol': position.symbol,
                    'type': 'BUY' if position.type == mt5.POSITION_TYPE_BUY else 'SELL',
                    'volume': float(position.volume),
                    'entry_price': float(position.price_open),
                    'current_price': current_price,
                    'profit': float(position.profit),
                    'profit_points': (current_price - position.price_open) * 10000 if position.type == mt5.POSITION_TYPE_BUY else (position.price_open - current_price) * 10000,
                    'sl': float(position.sl) if position.sl > 0 else None,
                    'tp': float(position.tp) if position.tp > 0 else None,
                    'duration': (datetime.now() - datetime.fromtimestamp(position.time)).total_seconds(),
                }
            else:
                logger.error(f"Unknown metric: {metric}")
                return None

        except Exception as e:
            logger.error(f"Error analyzing position: {e}")
            return None

    def get_position_stats(self) -> Optional[Dict]:
        """
        Get statistics for all open positions.

        Returns:
            Dict with position statistics

        Examples:
            >>> stats = mt5_trade.get_position_stats()
        """
        try:
            positions = self.get_positions()

            if positions is None or len(positions) == 0:
                return {
                    'total_positions': 0,
                    'total_volume': 0.0,
                    'total_profit': 0.0,
                }

            stats = {
                'total_positions': len(positions),
                'total_volume': float(positions['volume'].sum()),
                'total_profit': float(positions['profit'].sum()),
                'buy_positions': len(positions[positions['type'] == mt5.POSITION_TYPE_BUY]),
                'sell_positions': len(positions[positions['type'] == mt5.POSITION_TYPE_SELL]),
                'profitable_positions': len(positions[positions['profit'] > 0]),
                'losing_positions': len(positions[positions['profit'] < 0]),
                'symbols': positions['symbol'].unique().tolist(),
            }

            return stats

        except Exception as e:
            logger.error(f"Error getting position stats: {e}")
            return None

    def validate_request(self, request: Dict) -> Tuple[bool, str]:
        """
        Validate trade request.

        Args:
            request: Trade request dict

        Returns:
            Tuple of (is_valid, error_message)

        Examples:
            >>> valid, msg = mt5_trade.validate_request(request)
        """
        try:
            # Check required fields
            required = ['action', 'symbol', 'volume', 'type']
            for field in required:
                if field not in request:
                    return False, f"Missing required field: {field}"

            # Check volume
            if request['volume'] <= 0:
                return False, "Volume must be positive"

            # Check symbol exists
            symbol_info = mt5.symbol_info(request['symbol'])
            if symbol_info is None:
                return False, f"Symbol {request['symbol']} not found"

            # Check volume limits
            if request['volume'] < symbol_info.volume_min:
                return False, f"Volume below minimum ({symbol_info.volume_min})"

            if request['volume'] > symbol_info.volume_max:
                return False, f"Volume above maximum ({symbol_info.volume_max})"

            return True, "Request is valid"

        except Exception as e:
            logger.error(f"Error validating request: {e}")
            return False, str(e)

    def check_order(self, ticket: int) -> Optional[Dict]:
        """
        Check order status.

        Args:
            ticket: Order ticket number

        Returns:
            Dict with order info or None

        Examples:
            >>> order_info = mt5_trade.check_order(12345)
        """
        try:
            order = mt5.orders_get(ticket=ticket)

            if order is None or len(order) == 0:
                # Check if it's a deal (closed order)
                deal = mt5.history_deals_get(ticket=ticket)
                if deal and len(deal) > 0:
                    return {
                        'status': 'closed',
                        'ticket': ticket,
                        'deal': deal[0]._asdict()
                    }
                return None

            order = order[0]
            return {
                'status': 'open',
                'ticket': ticket,
                'order': order._asdict()
            }

        except Exception as e:
            logger.error(f"Error checking order: {e}")
            return None

    def get_summary(self) -> Dict[str, Any]:
        """
        Get trading summary.

        Returns:
            Dict with trading summary

        Examples:
            >>> summary = mt5_trade.get_summary()
        """
        try:
            summary = {}

            # Get positions
            positions = self.get_positions()
            if positions is not None:
                summary['positions'] = self.get_position_stats()
            else:
                summary['positions'] = {'total_positions': 0}

            # Get orders
            orders = self.get_orders()
            if orders is not None and len(orders) > 0:
                summary['orders'] = {
                    'total_orders': len(orders),
                    'symbols': orders['symbol'].unique().tolist(),
                }
            else:
                summary['orders'] = {'total_orders': 0}

            return summary

        except Exception as e:
            logger.error(f"Error getting summary: {e}")
            return {}

    def export(self, filepath: Union[str, Path], format: str = 'json') -> bool:
        """
        Export trading summary to file.

        Args:
            filepath: Output file path
            format: Export format ('json' or 'csv')

        Returns:
            True if successful, False otherwise

        Examples:
            >>> mt5_trade.export('trading_summary.json')
        """
        try:
            summary = self.get_summary()

            filepath = Path(filepath)
            filepath.parent.mkdir(parents=True, exist_ok=True)

            if format == 'json':
                with open(filepath, 'w') as f:
                    json.dump(summary, f, indent=2, default=str)
            elif format == 'csv':
                # Convert to DataFrame and export
                df = pd.DataFrame([summary])
                df.to_csv(filepath, index=False)
            else:
                logger.error(f"Unsupported format: {format}")
                return False

            logger.info(f"Exported trading summary to {filepath}")
            return True

        except Exception as e:
            logger.error(f"Error exporting: {e}")
            return False
