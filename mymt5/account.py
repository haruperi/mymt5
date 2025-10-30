"""MT5Account - Account information and management"""

from mylogger import logger
from typing import Optional, Dict, Any, Union
import MetaTrader5 as mt5
from datetime import datetime, timedelta


class MT5Account:
    """
    MT5Account class for managing account information and metrics.

    This class provides methods to retrieve account information, check account status,
    calculate account metrics, and export account data.
    """

    def __init__(self, client):
        """
        Initialize MT5Account with a client instance.

        Args:
            client: MT5Client instance for MT5 operations
        """
        logger.info("Initializing MT5Account")
        self.client = client
        self._account_info_cache = None
        self._cache_timestamp = None
        self._cache_duration = 1  # seconds

    def get(self, attribute: Optional[str] = None) -> Union[Any, Dict[str, Any]]:
        """
        Unified getter for account information.

        Args:
            attribute: Specific attribute to get ('balance', 'equity', 'margin', etc.)
                      If None, returns all account information as dict

        Returns:
            Requested attribute value or complete account info dict

        Raises:
            ValueError: If attribute doesn't exist
            RuntimeError: If failed to retrieve account info

        Examples:
            >>> account.get('balance')
            10000.0
            >>> account.get('equity')
            10500.0
            >>> account.get()  # Returns all info
            {'balance': 10000.0, 'equity': 10500.0, ...}
        """
        logger.info(f"Getting account info: attribute={attribute}")

        account_info = self._fetch_account_info()

        if attribute is None:
            return account_info

        if attribute not in account_info:
            logger.error(f"Invalid attribute: {attribute}")
            raise ValueError(f"Attribute '{attribute}' does not exist")

        return account_info[attribute]

    def _fetch_account_info(self) -> Dict[str, Any]:
        """
        Private method to fetch account information from MT5.
        Implements caching to reduce API calls.

        Returns:
            Dictionary with account information

        Raises:
            RuntimeError: If failed to retrieve account info
        """
        # Check cache
        if self._account_info_cache is not None and self._cache_timestamp is not None:
            elapsed = (datetime.now() - self._cache_timestamp).total_seconds()
            if elapsed < self._cache_duration:
                logger.debug("Returning cached account info")
                return self._account_info_cache

        logger.debug("Fetching fresh account info from MT5")
        account_info = mt5.account_info()

        if account_info is None:
            error_code, error_desc = mt5.last_error()
            logger.error(f"Failed to get account info: {error_code} - {error_desc}")
            raise RuntimeError(f"Failed to get account info: {error_code} - {error_desc}")

        # Convert to dictionary
        info_dict = {
            'login': account_info.login,
            'trade_mode': account_info.trade_mode,
            'leverage': account_info.leverage,
            'limit_orders': account_info.limit_orders,
            'margin_so_mode': account_info.margin_so_mode,
            'trade_allowed': account_info.trade_allowed,
            'trade_expert': account_info.trade_expert,
            'margin_mode': account_info.margin_mode,
            'currency_digits': account_info.currency_digits,
            'fifo_close': account_info.fifo_close,
            'balance': account_info.balance,
            'credit': account_info.credit,
            'profit': account_info.profit,
            'equity': account_info.equity,
            'margin': account_info.margin,
            'margin_free': account_info.margin_free,
            'margin_level': account_info.margin_level,
            'margin_so_call': account_info.margin_so_call,
            'margin_so_so': account_info.margin_so_so,
            'margin_initial': account_info.margin_initial,
            'margin_maintenance': account_info.margin_maintenance,
            'assets': account_info.assets,
            'liabilities': account_info.liabilities,
            'commission_blocked': account_info.commission_blocked,
            'name': account_info.name,
            'server': account_info.server,
            'currency': account_info.currency,
            'company': account_info.company,
        }

        # Update cache
        self._account_info_cache = info_dict
        self._cache_timestamp = datetime.now()

        logger.info("Account info retrieved successfully")
        return info_dict

    def check(self, status_type: str) -> bool:
        """
        Check account status.

        Args:
            status_type: Type of status to check:
                - 'demo': Is this a demo account?
                - 'authorized': Is account authorized for trading?
                - 'trade_allowed': Is trading allowed?
                - 'expert_allowed': Are Expert Advisors allowed?

        Returns:
            Boolean status result

        Raises:
            ValueError: If status_type is invalid

        Examples:
            >>> account.check('demo')
            True
            >>> account.check('trade_allowed')
            True
        """
        logger.info(f"Checking account status: {status_type}")

        valid_types = ['demo', 'authorized', 'trade_allowed', 'expert_allowed']
        if status_type not in valid_types:
            logger.error(f"Invalid status_type: {status_type}")
            raise ValueError(f"Invalid status_type. Must be one of {valid_types}")

        account_info = self._fetch_account_info()

        if status_type == 'demo':
            # trade_mode: 0 - demo, 1 - contest, 2 - real
            result = account_info['trade_mode'] == 0
        elif status_type == 'authorized':
            # If we can fetch account info, we're authorized
            result = True
        elif status_type == 'trade_allowed':
            result = account_info['trade_allowed']
        elif status_type == 'expert_allowed':
            result = account_info['trade_expert']

        logger.info(f"Status check {status_type}: {result}")
        return result

    def calculate(self, metric: str, **kwargs) -> Union[float, Dict[str, Any]]:
        """
        Calculate account metrics.

        Args:
            metric: Metric to calculate:
                - 'margin_level': Current margin level percentage
                - 'drawdown': Current drawdown (absolute or percentage)
                - 'health': Overall account health metrics
                - 'margin_required': Margin required for a trade
            **kwargs: Additional parameters depending on metric

        Returns:
            Calculated metric value or dictionary of metrics

        Examples:
            >>> account.calculate('margin_level')
            1500.0
            >>> account.calculate('drawdown', type='percent')
            5.2
            >>> account.calculate('margin_required', symbol='EURUSD', volume=1.0)
            1000.0
        """
        logger.info(f"Calculating metric: {metric}")

        valid_metrics = ['margin_level', 'drawdown', 'health', 'margin_required']
        if metric not in valid_metrics:
            logger.error(f"Invalid metric: {metric}")
            raise ValueError(f"Invalid metric. Must be one of {valid_metrics}")

        if metric == 'margin_level':
            return self._calculate_margin_level()
        elif metric == 'drawdown':
            return self._calculate_drawdown(**kwargs)
        elif metric == 'health':
            return self._calculate_health_metrics()
        elif metric == 'margin_required':
            return self._calculate_margin_required(**kwargs)

    def _calculate_margin_level(self) -> float:
        """
        Calculate current margin level.

        Returns:
            Margin level as percentage (equity/margin * 100)
            Returns 0 if margin is 0
        """
        account_info = self._fetch_account_info()
        margin = account_info['margin']

        if margin == 0:
            # If there are no open positions, margin level is effectively infinite
            try:
                positions = mt5.positions_total()
            except Exception:
                positions = 0
            if positions == 0:
                logger.info("No open positions and margin is 0; returning infinite margin level")
                return float('inf')
            logger.warning("Margin is 0 with open positions; returning 0 for margin level")
            return 0.0

        margin_level = (account_info['equity'] / margin) * 100
        logger.info(f"Calculated margin level: {margin_level:.2f}%")
        return margin_level

    def _calculate_drawdown(self, type: str = 'percent') -> float:
        """
        Calculate current drawdown.

        Args:
            type: 'percent' or 'absolute'

        Returns:
            Drawdown value
        """
        account_info = self._fetch_account_info()
        balance = account_info['balance']
        equity = account_info['equity']

        if type == 'absolute':
            drawdown = balance - equity
        else:  # percent
            if balance == 0:
                drawdown = 0.0
            else:
                drawdown = ((balance - equity) / balance) * 100

        logger.info(f"Calculated drawdown ({type}): {drawdown:.2f}")
        return drawdown

    def _calculate_health_metrics(self) -> Dict[str, Any]:
        """
        Calculate overall account health metrics.

        Returns:
            Dictionary with various health indicators
        """
        account_info = self._fetch_account_info()

        balance = account_info['balance']
        equity = account_info['equity']
        margin = account_info['margin']
        margin_free = account_info['margin_free']
        profit = account_info['profit']

        # Calculate metrics (handles 0-margin internally, may return inf)
        margin_level = self._calculate_margin_level()
        drawdown_percent = self._calculate_drawdown(type='percent')

        # Determine health status
        if margin_level > 200:
            health_status = 'excellent'
        elif margin_level > 100:
            health_status = 'good'
        elif margin_level > 50:
            health_status = 'warning'
        else:
            health_status = 'critical'

        health_metrics = {
            'balance': balance,
            'equity': equity,
            'profit': profit,
            'margin': margin,
            'margin_free': margin_free,
            'margin_level': margin_level,
            'drawdown_percent': drawdown_percent,
            'health_status': health_status,
        }

        logger.info(f"Health metrics calculated: status={health_status}")
        return health_metrics

    def _calculate_margin_required(self, symbol: str, volume: float, **kwargs) -> float:
        """
        Calculate margin required for a trade.

        Args:
            symbol: Trading symbol
            volume: Trade volume in lots

        Returns:
            Required margin amount

        Raises:
            RuntimeError: If calculation fails
        """
        logger.info(f"Calculating margin required for {symbol}, volume={volume}")

        # Ensure symbol is selected/visible in Market Watch
        try:
            if not mt5.symbol_select(symbol, True):
                logger.warning(f"Symbol {symbol} was not selected; attempting to select failed")
        except Exception as e:
            logger.warning(f"Exception while selecting symbol {symbol}: {e}")

        # Get symbol info for pricing
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            code, desc = mt5.last_error()
            logger.error(f"Failed to get symbol info for {symbol}: {code} - {desc}")
            raise RuntimeError(f"Failed to get symbol info for {symbol}: {code} - {desc}")

        # Determine a robust price to use: ask -> bid -> tick -> last
        price = None
        try:
            if getattr(symbol_info, 'ask', 0) and symbol_info.ask > 0:
                price = symbol_info.ask
            elif getattr(symbol_info, 'bid', 0) and symbol_info.bid > 0:
                price = symbol_info.bid
            else:
                tick = mt5.symbol_info_tick(symbol)
                if tick is not None:
                    if getattr(tick, 'ask', 0) and tick.ask > 0:
                        price = tick.ask
                    elif getattr(tick, 'bid', 0) and tick.bid > 0:
                        price = tick.bid
                    elif getattr(tick, 'last', 0) and tick.last > 0:
                        price = tick.last
            if price is None and getattr(symbol_info, 'last', 0) and symbol_info.last > 0:
                price = symbol_info.last
        except Exception as e:
            logger.warning(f"Exception while selecting price for {symbol}: {e}")

        if price is None or price <= 0:
            # Fallback 1: try recent ticks within last day
            try:
                since = datetime.now() - timedelta(days=1)
                ticks = mt5.copy_ticks_from(symbol, since, 1000, mt5.COPY_TICKS_INFO)
                if ticks is not None and len(ticks) > 0:
                    # Find the last tick with usable price
                    for t in reversed(ticks):
                        ask_v = t['ask'] if 'ask' in t.dtype.names else 0
                        bid_v = t['bid'] if 'bid' in t.dtype.names else 0
                        last_v = t['last'] if 'last' in t.dtype.names else 0
                        if ask_v and ask_v > 0:
                            price = float(ask_v)
                            break
                        if bid_v and bid_v > 0:
                            price = float(bid_v)
                            break
                        if last_v and last_v > 0:
                            price = float(last_v)
                            break
            except Exception as e:
                logger.warning(f"Exception while fetching recent ticks for {symbol}: {e}")

        if price is None or price <= 0:
            # Fallback 2: try last M1 candle close
            try:
                rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 1)
                if rates is not None and len(rates) > 0 and 'close' in rates.dtype.names:
                    close_v = rates[0]['close']
                    if close_v and close_v > 0:
                        price = float(close_v)
            except Exception as e:
                logger.warning(f"Exception while fetching M1 close for {symbol}: {e}")

        if price is None or price <= 0:
            code, desc = mt5.last_error()
            logger.error(f"No valid price available for {symbol}; last_error={code} - {desc}")
            raise RuntimeError(f"No valid price available for {symbol}")

        # Calculate margin using MT5 function
        action = mt5.ORDER_TYPE_BUY  # Use buy as default for calculation
        margin = mt5.order_calc_margin(action, symbol, volume, price)
        if margin is None:
            code, desc = mt5.last_error()
            logger.error(f"Failed to calculate margin for {symbol} at price {price}: {code} - {desc}")
            raise RuntimeError(f"Failed to calculate margin: {code} - {desc}")

        logger.info(f"Required margin: {margin}")
        return margin

    def validate_credentials(self, login: int, password: str, server: str) -> bool:
        """
        Validate account credentials.

        Args:
            login: Account login number
            password: Account password
            server: Server name

        Returns:
            True if credentials are valid, False otherwise
        """
        logger.info(f"Validating credentials for login={login}, server={server}")

        try:
            # Try to authorize with provided credentials
            authorized = mt5.login(login, password, server)

            if authorized:
                logger.info("Credentials validated successfully")
                return True
            else:
                logger.warning("Invalid credentials")
                return False
        except Exception as e:
            logger.error(f"Error validating credentials: {e}")
            return False

    def get_summary(self) -> Dict[str, Any]:
        """
        Get account summary with key information.

        Returns:
            Dictionary with account summary
        """
        logger.info("Getting account summary")

        account_info = self._fetch_account_info()
        health = self._calculate_health_metrics()

        summary = {
            'login': account_info['login'],
            'name': account_info['name'],
            'server': account_info['server'],
            'company': account_info['company'],
            'currency': account_info['currency'],
            'balance': account_info['balance'],
            'equity': account_info['equity'],
            'profit': account_info['profit'],
            'margin': account_info['margin'],
            'margin_free': account_info['margin_free'],
            'margin_level': health['margin_level'],
            'leverage': account_info['leverage'],
            'trade_mode': 'Demo' if account_info['trade_mode'] == 0 else 'Real',
            'trade_allowed': account_info['trade_allowed'],
            'health_status': health['health_status'],
        }

        logger.info("Account summary generated")
        return summary

    def export(self, format: str = 'dict', filepath: Optional[str] = None) -> Union[Dict, str]:
        """
        Export account information.

        Args:
            format: Export format ('dict', 'json', 'csv')
            filepath: Optional file path to save export

        Returns:
            Exported data as dict or JSON string

        Examples:
            >>> account.export('dict')
            {...}
            >>> account.export('json', 'account_info.json')
            'Exported to account_info.json'
        """
        logger.info(f"Exporting account info: format={format}")

        account_info = self._fetch_account_info()

        if format == 'dict':
            return account_info
        elif format == 'json':
            import json
            json_str = json.dumps(account_info, indent=2, default=str)

            if filepath:
                with open(filepath, 'w') as f:
                    f.write(json_str)
                logger.info(f"Account info exported to {filepath}")
                return f"Exported to {filepath}"
            return json_str
        elif format == 'csv':
            import csv

            if not filepath:
                filepath = 'account_info.csv'

            with open(filepath, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Field', 'Value'])
                for key, value in account_info.items():
                    writer.writerow([key, value])

            logger.info(f"Account info exported to {filepath}")
            return f"Exported to {filepath}"
        else:
            logger.error(f"Invalid export format: {format}")
            raise ValueError(f"Invalid format. Must be 'dict', 'json', or 'csv'")


logger.info("MT5Account module loaded")
