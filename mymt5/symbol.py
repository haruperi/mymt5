"""MT5Symbol - Symbol information, management and validation"""

from mylogger import logger
from typing import Optional, Dict, Any, Union, List, Tuple
import MetaTrader5 as mt5
from datetime import datetime
import json


class MT5Symbol:
    """
    MT5Symbol class for managing symbol information and operations.

    This class provides methods to discover symbols, manage market watch,
    retrieve symbol information, check status, get real-time prices,
    access market depth, manage subscriptions, validate symbols and volumes,
    and export symbol data.
    """

    def __init__(self, client):
        """
        Initialize MT5Symbol with a client instance.

        Args:
            client: MT5Client instance for MT5 operations
        """
        logger.info("Initializing MT5Symbol")
        self.client = client
        self._symbol_info_cache = {}
        self._cache_timestamp = {}
        self._cache_duration = 1  # seconds
        self._subscriptions = set()

    # ============================================================
    # 1. Symbol Discovery
    # ============================================================

    def get_symbols(self, filter_type: str = 'all', group: Optional[str] = None) -> List[str]:
        """
        Get list of symbols based on filter type.

        Args:
            filter_type: Type of filter to apply:
                - 'all': All available symbols
                - 'market_watch': Symbols in Market Watch
                - 'group': Symbols by group pattern
                - 'search': Search symbols by pattern
            group: Group or search pattern (required for 'group' and 'search')

        Returns:
            List of symbol names

        Raises:
            ValueError: If filter_type is invalid or group is missing

        Examples:
            >>> symbol.get_symbols('all')
            ['EURUSD', 'GBPUSD', ...]
            >>> symbol.get_symbols('market_watch')
            ['EURUSD', 'GBPUSD']
            >>> symbol.get_symbols('group', 'Forex*')
            ['EURUSD', 'GBPUSD', ...]
        """
        logger.info(f"Getting symbols: filter_type={filter_type}, group={group}")

        valid_types = ['all', 'market_watch', 'group', 'search']
        if filter_type not in valid_types:
            logger.error(f"Invalid filter_type: {filter_type}")
            raise ValueError(f"Invalid filter_type. Must be one of {valid_types}")

        if filter_type in ['group', 'search'] and not group:
            logger.error(f"Group pattern required for filter_type={filter_type}")
            raise ValueError(f"Group pattern required for filter_type '{filter_type}'")

        if filter_type == 'all':
            symbols_tuple = mt5.symbols_get()
            if symbols_tuple is None:
                logger.warning("No symbols retrieved")
                return []
            symbols = [s.name for s in symbols_tuple]

        elif filter_type == 'market_watch':
            symbols_tuple = mt5.symbols_get()
            if symbols_tuple is None:
                logger.warning("No symbols retrieved")
                return []
            # Filter only visible symbols
            symbols = [s.name for s in symbols_tuple if s.visible]

        elif filter_type == 'group':
            symbols_tuple = mt5.symbols_get(group=group)
            if symbols_tuple is None:
                logger.warning(f"No symbols found for group: {group}")
                return []
            symbols = [s.name for s in symbols_tuple]

        elif filter_type == 'search':
            # Search in symbol names
            all_symbols = mt5.symbols_get()
            if all_symbols is None:
                logger.warning("No symbols retrieved")
                return []
            import fnmatch
            symbols = [s.name for s in all_symbols if fnmatch.fnmatch(s.name, group)]

        logger.info(f"Found {len(symbols)} symbols")
        return symbols

    # ============================================================
    # 2. Market Watch Management
    # ============================================================

    def initialize(self, symbol: str) -> bool:
        """
        Initialize symbol for trading (enable in Market Watch).

        Args:
            symbol: Symbol name

        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Initializing symbol: {symbol}")

        result = mt5.symbol_select(symbol, True)
        if result:
            logger.info(f"Symbol {symbol} initialized successfully")
        else:
            logger.error(f"Failed to initialize symbol: {symbol}")

        return result

    def manage(self, action: str, symbol: str) -> bool:
        """
        Manage symbol in Market Watch.

        Args:
            action: Action to perform:
                - 'add': Add symbol to Market Watch
                - 'remove': Remove symbol from Market Watch
                - 'select': Select symbol (enable)
                - 'deselect': Deselect symbol (disable)
            symbol: Symbol name

        Returns:
            True if successful, False otherwise

        Raises:
            ValueError: If action is invalid

        Examples:
            >>> symbol.manage('add', 'EURUSD')
            True
            >>> symbol.manage('remove', 'GBPUSD')
            True
        """
        logger.info(f"Managing symbol: action={action}, symbol={symbol}")

        valid_actions = ['add', 'remove', 'select', 'deselect']
        if action not in valid_actions:
            logger.error(f"Invalid action: {action}")
            raise ValueError(f"Invalid action. Must be one of {valid_actions}")

        if action in ['add', 'select']:
            result = mt5.symbol_select(symbol, True)
        else:  # 'remove', 'deselect'
            result = mt5.symbol_select(symbol, False)

        if result:
            logger.info(f"Action {action} successful for {symbol}")
        else:
            logger.error(f"Action {action} failed for {symbol}")

        return result

    # ============================================================
    # 3. Symbol Information
    # ============================================================

    def get_info(self, symbol: str, attribute: Optional[str] = None) -> Union[Any, Dict[str, Any]]:
        """
        Unified getter for symbol information.

        Args:
            symbol: Symbol name
            attribute: Specific attribute to get (e.g., 'bid', 'ask', 'spread', etc.)
                      If None, returns all symbol information as dict

        Returns:
            Requested attribute value or complete symbol info dict

        Raises:
            ValueError: If attribute doesn't exist
            RuntimeError: If failed to retrieve symbol info

        Examples:
            >>> symbol.get_info('EURUSD', 'bid')
            1.09234
            >>> symbol.get_info('EURUSD', 'ask')
            1.09245
            >>> symbol.get_info('EURUSD')  # Returns all info
            {'bid': 1.09234, 'ask': 1.09245, ...}
        """
        logger.info(f"Getting symbol info: symbol={symbol}, attribute={attribute}")

        symbol_info = self._fetch_symbol_info(symbol)

        if attribute is None:
            return symbol_info

        if attribute not in symbol_info:
            logger.error(f"Invalid attribute: {attribute}")
            raise ValueError(f"Attribute '{attribute}' does not exist")

        return symbol_info[attribute]

    def _fetch_symbol_info(self, symbol: str) -> Dict[str, Any]:
        """
        Private method to fetch symbol information from MT5.
        Implements caching to reduce API calls.

        Args:
            symbol: Symbol name

        Returns:
            Dictionary with symbol information

        Raises:
            RuntimeError: If failed to retrieve symbol info
        """
        # Check cache
        if symbol in self._symbol_info_cache and symbol in self._cache_timestamp:
            elapsed = (datetime.now() - self._cache_timestamp[symbol]).total_seconds()
            if elapsed < self._cache_duration:
                logger.debug(f"Returning cached symbol info for {symbol}")
                return self._symbol_info_cache[symbol]

        logger.debug(f"Fetching fresh symbol info from MT5 for {symbol}")
        symbol_info = mt5.symbol_info(symbol)

        if symbol_info is None:
            error_code, error_desc = mt5.last_error()
            logger.error(f"Failed to get symbol info for {symbol}: {error_code} - {error_desc}")
            raise RuntimeError(f"Failed to get symbol info for {symbol}: {error_code} - {error_desc}")

        # Convert to dictionary
        info_dict = {
            'name': symbol_info.name,
            'custom': symbol_info.custom,
            'chart_mode': symbol_info.chart_mode,
            'select': symbol_info.select,
            'visible': symbol_info.visible,
            'session_deals': symbol_info.session_deals,
            'session_buy_orders': symbol_info.session_buy_orders,
            'session_sell_orders': symbol_info.session_sell_orders,
            'volume': symbol_info.volume,
            'volumehigh': symbol_info.volumehigh,
            'volumelow': symbol_info.volumelow,
            'time': symbol_info.time,
            'digits': symbol_info.digits,
            'spread': symbol_info.spread,
            'spread_float': symbol_info.spread_float,
            'ticks_bookdepth': symbol_info.ticks_bookdepth,
            'trade_calc_mode': symbol_info.trade_calc_mode,
            'trade_mode': symbol_info.trade_mode,
            'start_time': symbol_info.start_time,
            'expiration_time': symbol_info.expiration_time,
            'trade_stops_level': symbol_info.trade_stops_level,
            'trade_freeze_level': symbol_info.trade_freeze_level,
            'trade_exemode': symbol_info.trade_exemode,
            'swap_mode': symbol_info.swap_mode,
            'swap_rollover3days': symbol_info.swap_rollover3days,
            'margin_hedged_use_leg': symbol_info.margin_hedged_use_leg,
            'expiration_mode': symbol_info.expiration_mode,
            'filling_mode': symbol_info.filling_mode,
            'order_mode': symbol_info.order_mode,
            'order_gtc_mode': symbol_info.order_gtc_mode,
            'option_mode': symbol_info.option_mode,
            'option_right': symbol_info.option_right,
            'bid': symbol_info.bid,
            'bidhigh': symbol_info.bidhigh,
            'bidlow': symbol_info.bidlow,
            'ask': symbol_info.ask,
            'askhigh': symbol_info.askhigh,
            'asklow': symbol_info.asklow,
            'last': symbol_info.last,
            'lasthigh': symbol_info.lasthigh,
            'lastlow': symbol_info.lastlow,
            'volume_real': symbol_info.volume_real,
            'volumehigh_real': symbol_info.volumehigh_real,
            'volumelow_real': symbol_info.volumelow_real,
            'option_strike': symbol_info.option_strike,
            'point': symbol_info.point,
            'trade_tick_value': symbol_info.trade_tick_value,
            'trade_tick_value_profit': symbol_info.trade_tick_value_profit,
            'trade_tick_value_loss': symbol_info.trade_tick_value_loss,
            'trade_tick_size': symbol_info.trade_tick_size,
            'trade_contract_size': symbol_info.trade_contract_size,
            'trade_accrued_interest': symbol_info.trade_accrued_interest,
            'trade_face_value': symbol_info.trade_face_value,
            'trade_liquidity_rate': symbol_info.trade_liquidity_rate,
            'volume_min': symbol_info.volume_min,
            'volume_max': symbol_info.volume_max,
            'volume_step': symbol_info.volume_step,
            'volume_limit': symbol_info.volume_limit,
            'swap_long': symbol_info.swap_long,
            'swap_short': symbol_info.swap_short,
            'margin_initial': symbol_info.margin_initial,
            'margin_maintenance': symbol_info.margin_maintenance,
            'session_volume': symbol_info.session_volume,
            'session_turnover': symbol_info.session_turnover,
            'session_interest': symbol_info.session_interest,
            'session_buy_orders_volume': symbol_info.session_buy_orders_volume,
            'session_sell_orders_volume': symbol_info.session_sell_orders_volume,
            'session_open': symbol_info.session_open,
            'session_close': symbol_info.session_close,
            'session_aw': symbol_info.session_aw,
            'session_price_settlement': symbol_info.session_price_settlement,
            'session_price_limit_min': symbol_info.session_price_limit_min,
            'session_price_limit_max': symbol_info.session_price_limit_max,
            'margin_hedged': symbol_info.margin_hedged,
            'price_change': symbol_info.price_change,
            'price_volatility': symbol_info.price_volatility,
            'price_theoretical': symbol_info.price_theoretical,
            'price_greeks_delta': symbol_info.price_greeks_delta,
            'price_greeks_theta': symbol_info.price_greeks_theta,
            'price_greeks_gamma': symbol_info.price_greeks_gamma,
            'price_greeks_vega': symbol_info.price_greeks_vega,
            'price_greeks_rho': symbol_info.price_greeks_rho,
            'price_greeks_omega': symbol_info.price_greeks_omega,
            'price_sensitivity': symbol_info.price_sensitivity,
            'basis': symbol_info.basis,
            'category': symbol_info.category,
            'currency_base': symbol_info.currency_base,
            'currency_profit': symbol_info.currency_profit,
            'currency_margin': symbol_info.currency_margin,
            'bank': symbol_info.bank,
            'description': symbol_info.description,
            'exchange': symbol_info.exchange,
            'formula': symbol_info.formula,
            'isin': symbol_info.isin,
            'name': symbol_info.name,
            'page': symbol_info.page,
            'path': symbol_info.path,
        }

        # Update cache
        self._update_cache(symbol, info_dict)

        logger.info(f"Symbol info retrieved successfully for {symbol}")
        return info_dict

    def _update_cache(self, symbol: str, info_dict: Dict[str, Any]):
        """
        Update the symbol info cache.

        Args:
            symbol: Symbol name
            info_dict: Symbol information dictionary
        """
        self._symbol_info_cache[symbol] = info_dict
        self._cache_timestamp[symbol] = datetime.now()
        logger.debug(f"Cache updated for {symbol}")

    # ============================================================
    # 4. Symbol Status
    # ============================================================

    def check(self, symbol: str, status_type: str) -> bool:
        """
        Check symbol status.

        Args:
            symbol: Symbol name
            status_type: Type of status to check:
                - 'available': Is symbol available in MT5?
                - 'visible': Is symbol visible in Market Watch?
                - 'tradable': Can we trade this symbol?
                - 'market_open': Is market currently open?

        Returns:
            Boolean status result

        Raises:
            ValueError: If status_type is invalid

        Examples:
            >>> symbol.check('EURUSD', 'available')
            True
            >>> symbol.check('EURUSD', 'tradable')
            True
        """
        logger.info(f"Checking symbol status: symbol={symbol}, status_type={status_type}")

        valid_types = ['available', 'visible', 'tradable', 'market_open']
        if status_type not in valid_types:
            logger.error(f"Invalid status_type: {status_type}")
            raise ValueError(f"Invalid status_type. Must be one of {valid_types}")

        try:
            symbol_info = self._fetch_symbol_info(symbol)

            if status_type == 'available':
                result = symbol_info is not None
            elif status_type == 'visible':
                result = symbol_info['visible']
            elif status_type == 'tradable':
                # trade_mode: 0-disabled, 1-long only, 2-short only, 3-close only, 4-full access
                result = symbol_info['trade_mode'] in [1, 2, 4]
            elif status_type == 'market_open':
                # Check if there's recent price activity
                current_time = datetime.now()
                symbol_time = datetime.fromtimestamp(symbol_info['time'])
                # Market considered open if last price update was within 1 minute
                result = (current_time - symbol_time).total_seconds() < 60

            logger.info(f"Status check {status_type} for {symbol}: {result}")
            return result

        except RuntimeError:
            logger.warning(f"Symbol {symbol} not available")
            return False

    # ============================================================
    # 5. Real-Time Prices
    # ============================================================

    def get_price(self, symbol: str, price_type: str = 'current') -> Union[float, Dict[str, float]]:
        """
        Get real-time price for symbol.

        Args:
            symbol: Symbol name
            price_type: Type of price to get:
                - 'current': Current bid/ask prices
                - 'bid': Current bid price
                - 'ask': Current ask price
                - 'last': Last deal price

        Returns:
            Price value or dict with bid/ask for 'current'

        Raises:
            ValueError: If price_type is invalid

        Examples:
            >>> symbol.get_price('EURUSD', 'bid')
            1.09234
            >>> symbol.get_price('EURUSD', 'current')
            {'bid': 1.09234, 'ask': 1.09245, 'spread': 0.00011}
        """
        logger.info(f"Getting price: symbol={symbol}, price_type={price_type}")

        valid_types = ['current', 'bid', 'ask', 'last']
        if price_type not in valid_types:
            logger.error(f"Invalid price_type: {price_type}")
            raise ValueError(f"Invalid price_type. Must be one of {valid_types}")

        symbol_info = self._fetch_symbol_info(symbol)

        if price_type == 'bid':
            price = symbol_info['bid']
        elif price_type == 'ask':
            price = symbol_info['ask']
        elif price_type == 'last':
            price = symbol_info['last']
        elif price_type == 'current':
            bid = symbol_info['bid']
            ask = symbol_info['ask']
            spread = ask - bid
            price = {
                'bid': bid,
                'ask': ask,
                'spread': spread,
                'time': symbol_info['time']
            }

        logger.info(f"Price retrieved for {symbol}")
        return price

    # ============================================================
    # 6. Market Depth
    # ============================================================

    def get_depth(self, symbol: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get market depth (DOM - Depth of Market).

        Args:
            symbol: Symbol name

        Returns:
            List of market depth entries or None if not available

        Examples:
            >>> symbol.get_depth('EURUSD')
            [{'type': 1, 'price': 1.09234, 'volume': 100}, ...]
        """
        logger.info(f"Getting market depth for {symbol}")

        # Ensure symbol is selected
        mt5.symbol_select(symbol, True)

        depth = mt5.market_book_get(symbol)
        if depth is None or len(depth) == 0:
            logger.warning(f"No market depth available for {symbol}")
            return None

        depth_list = []
        for item in depth:
            depth_list.append({
                'type': item.type,  # 1-buy, 2-sell
                'price': item.price,
                'volume': item.volume,
                'volume_real': item.volume_real
            })

        logger.info(f"Market depth retrieved for {symbol}: {len(depth_list)} entries")
        return depth_list

    # ============================================================
    # 7. Subscriptions
    # ============================================================

    def subscribe(self, symbol: str) -> bool:
        """
        Subscribe to market depth updates for symbol.

        Args:
            symbol: Symbol name

        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Subscribing to market depth: {symbol}")

        result = mt5.market_book_add(symbol)
        if result:
            self._subscriptions.add(symbol)
            logger.info(f"Successfully subscribed to {symbol}")
        else:
            logger.error(f"Failed to subscribe to {symbol}")

        return result

    def unsubscribe(self, symbol: str) -> bool:
        """
        Unsubscribe from market depth updates for symbol.

        Args:
            symbol: Symbol name

        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Unsubscribing from market depth: {symbol}")

        result = mt5.market_book_release(symbol)
        if result:
            self._subscriptions.discard(symbol)
            logger.info(f"Successfully unsubscribed from {symbol}")
        else:
            logger.error(f"Failed to unsubscribe from {symbol}")

        return result

    # ============================================================
    # 8. Validation
    # ============================================================

    def validate(self, symbol: str, validation_type: str, **kwargs) -> Tuple[bool, str]:
        """
        Validate symbol or volume.

        Args:
            symbol: Symbol name
            validation_type: Type of validation:
                - 'exists': Check if symbol exists
                - 'tradable': Check if symbol is tradable
                - 'volume': Validate trading volume
            **kwargs: Additional parameters for validation

        Returns:
            Tuple of (is_valid: bool, message: str)

        Examples:
            >>> symbol.validate('EURUSD', 'exists')
            (True, 'Symbol exists')
            >>> symbol.validate('EURUSD', 'volume', volume=1.0)
            (True, 'Volume is valid')
        """
        logger.info(f"Validating symbol: symbol={symbol}, validation_type={validation_type}")

        valid_types = ['exists', 'tradable', 'volume']
        if validation_type not in valid_types:
            logger.error(f"Invalid validation_type: {validation_type}")
            raise ValueError(f"Invalid validation_type. Must be one of {valid_types}")

        if validation_type == 'exists':
            try:
                self._fetch_symbol_info(symbol)
                return (True, "Symbol exists")
            except RuntimeError:
                return (False, f"Symbol '{symbol}' does not exist")

        elif validation_type == 'tradable':
            try:
                symbol_info = self._fetch_symbol_info(symbol)
                trade_mode = symbol_info['trade_mode']
                if trade_mode in [1, 2, 4]:
                    return (True, "Symbol is tradable")
                else:
                    return (False, f"Symbol is not tradable (trade_mode={trade_mode})")
            except RuntimeError:
                return (False, f"Symbol '{symbol}' does not exist")

        elif validation_type == 'volume':
            volume = kwargs.get('volume')
            if volume is None:
                return (False, "Volume parameter required")
            return self.validate_volume(symbol, volume)

    def validate_volume(self, symbol: str, volume: float) -> Tuple[bool, str]:
        """
        Validate if volume is valid for the symbol.

        Args:
            symbol: Symbol name
            volume: Volume in lots

        Returns:
            Tuple of (is_valid: bool, message: str)

        Examples:
            >>> symbol.validate_volume('EURUSD', 1.0)
            (True, 'Volume is valid')
            >>> symbol.validate_volume('EURUSD', 0.001)
            (False, 'Volume below minimum (0.01)')
        """
        logger.info(f"Validating volume: symbol={symbol}, volume={volume}")

        try:
            symbol_info = self._fetch_symbol_info(symbol)
            volume_min = symbol_info['volume_min']
            volume_max = symbol_info['volume_max']
            volume_step = symbol_info['volume_step']

            # Check minimum
            if volume < volume_min:
                msg = f"Volume below minimum ({volume_min})"
                logger.warning(msg)
                return (False, msg)

            # Check maximum
            if volume > volume_max:
                msg = f"Volume above maximum ({volume_max})"
                logger.warning(msg)
                return (False, msg)

            # Check step
            # Volume must be a multiple of volume_step
            remainder = (volume - volume_min) % volume_step
            if abs(remainder) > 1e-10:  # Small tolerance for floating point
                msg = f"Volume not aligned with step ({volume_step})"
                logger.warning(msg)
                return (False, msg)

            logger.info("Volume is valid")
            return (True, "Volume is valid")

        except RuntimeError as e:
            msg = f"Failed to validate volume: {str(e)}"
            logger.error(msg)
            return (False, msg)

    # ============================================================
    # 9. Utility
    # ============================================================

    def get_summary(self, symbol: str) -> Dict[str, Any]:
        """
        Get symbol summary with key information.

        Args:
            symbol: Symbol name

        Returns:
            Dictionary with symbol summary
        """
        logger.info(f"Getting symbol summary for {symbol}")

        symbol_info = self._fetch_symbol_info(symbol)

        summary = {
            'name': symbol_info['name'],
            'description': symbol_info['description'],
            'bid': symbol_info['bid'],
            'ask': symbol_info['ask'],
            'spread': symbol_info['spread'],
            'digits': symbol_info['digits'],
            'point': symbol_info['point'],
            'volume_min': symbol_info['volume_min'],
            'volume_max': symbol_info['volume_max'],
            'volume_step': symbol_info['volume_step'],
            'contract_size': symbol_info['trade_contract_size'],
            'tick_value': symbol_info['trade_tick_value'],
            'tick_size': symbol_info['trade_tick_size'],
            'swap_long': symbol_info['swap_long'],
            'swap_short': symbol_info['swap_short'],
            'trade_mode': symbol_info['trade_mode'],
            'visible': symbol_info['visible'],
            'currency_base': symbol_info['currency_base'],
            'currency_profit': symbol_info['currency_profit'],
            'currency_margin': symbol_info['currency_margin'],
        }

        logger.info(f"Symbol summary generated for {symbol}")
        return summary

    def export_list(self, symbols: Optional[List[str]] = None,
                    format: str = 'dict', filepath: Optional[str] = None) -> Union[List[Dict], str]:
        """
        Export list of symbols with their information.

        Args:
            symbols: List of symbol names (if None, exports all market watch symbols)
            format: Export format ('dict', 'json', 'csv')
            filepath: Optional file path to save export

        Returns:
            Exported data as list of dicts or JSON string

        Examples:
            >>> symbol.export_list(['EURUSD', 'GBPUSD'], 'dict')
            [{'name': 'EURUSD', ...}, {'name': 'GBPUSD', ...}]
            >>> symbol.export_list(format='json', filepath='symbols.json')
            'Exported to symbols.json'
        """
        logger.info(f"Exporting symbol list: format={format}")

        if symbols is None:
            symbols = self.get_symbols('market_watch')

        symbol_list = []
        for sym in symbols:
            try:
                summary = self.get_summary(sym)
                symbol_list.append(summary)
            except Exception as e:
                logger.warning(f"Failed to get summary for {sym}: {e}")
                continue

        if format == 'dict':
            return symbol_list
        elif format == 'json':
            json_str = json.dumps(symbol_list, indent=2, default=str)

            if filepath:
                with open(filepath, 'w') as f:
                    f.write(json_str)
                logger.info(f"Symbol list exported to {filepath}")
                return f"Exported to {filepath}"
            return json_str
        elif format == 'csv':
            import csv

            if not filepath:
                filepath = 'symbol_list.csv'

            if len(symbol_list) > 0:
                with open(filepath, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=symbol_list[0].keys())
                    writer.writeheader()
                    writer.writerows(symbol_list)

                logger.info(f"Symbol list exported to {filepath}")
                return f"Exported to {filepath}"
            else:
                logger.warning("No symbols to export")
                return "No symbols to export"
        else:
            logger.error(f"Invalid export format: {format}")
            raise ValueError(f"Invalid format. Must be 'dict', 'json', or 'csv'")


logger.info("MT5Symbol module loaded")
