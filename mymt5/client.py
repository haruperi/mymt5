"""
MT5 Trading System - Client Module

This module provides the main client class for connecting to and interacting with
the MetaTrader 5 terminal. It handles connection management, authentication,
auto-reconnection, multi-account support, and event handling.
"""

from mylogger import logger
import MetaTrader5 as mt5
from typing import Optional, Dict, Any, Callable, List, Tuple
from datetime import datetime
import time
import json
import os
from pathlib import Path
from .enums import ConnectionState


logger.info("Loading client module")


class MT5Client:
    """
    Main client class for MetaTrader 5 terminal interaction.

    This class provides comprehensive connection management, authentication,
    auto-reconnection capabilities, multi-account support, and event handling
    for the MT5 trading system.

    Attributes:
        connection_state (ConnectionState): Current connection state
        login (int): Account login number
        password (str): Account password
        server (str): MT5 server name
        path (str): Path to MT5 terminal executable
        timeout (int): Connection timeout in seconds
        auto_reconnect_enabled (bool): Whether auto-reconnection is enabled
        retry_attempts (int): Number of retry attempts for reconnection
        retry_delay (int): Delay between retry attempts in seconds

    Example:
        >>> client = MT5Client()
        >>> client.initialize(login=12345, password="pass", server="Server-Demo")
        >>> if client.is_connected():
        ...     print("Connected successfully")
        >>> client.shutdown()
    """

    def __init__(
        self,
        timeout: int = 60000,
        portable: bool = False
    ):
        """
        Initialize the MT5Client instance.

        Args:
            timeout: Connection timeout in milliseconds (default: 60000)
            portable: Whether to use portable mode (default: False)

        Example:
            >>> client = MT5Client(
            ...     path="C:/Program Files/MT5/terminal64.exe",
            ...     timeout=30000
            ... )
        """
        logger.info("Initializing MT5Client")

        # Connection attributes
        self.connection_state: ConnectionState = ConnectionState.DISCONNECTED
        self.timeout: int = timeout
        self.portable: bool = portable

        # Authentication attributes
        self.account_login: int = 0
        self.account_password: str = ""
        self.account_server: str = ""
        self.path: str = ""

        # Auto-reconnection attributes
        self.auto_reconnect_enabled: bool = False
        self.retry_attempts: int = 3
        self.retry_delay: int = 5
        self._reconnection_in_progress: bool = False

        # Configuration attributes
        self.config: Dict[str, Any] = {}
        self.config_path: str = ""

        # Multi-account support
        self.accounts: Dict[str, Dict[str, Any]] = {}
        self.current_account: str = ""

        # Event system
        self._event_handlers: Dict[str, List[Callable]] = {
            'connect': [],
            'disconnect': [],
            'error': [],
            'reconnect': [],
            'account_switch': []
        }

        # Connection statistics
        self._connection_attempts: int = 0
        self._successful_connections: int = 0
        self._failed_connections: int = 0
        self._last_connection_time: Optional[datetime] = None
        self._total_connection_time: float = 0

        # Error tracking
        self._last_error: Optional[Tuple[int, str]] = None
        self._error_count: int = 0

        logger.success("MT5Client initialized successfully")

    # =============================================================================
    # CONNECTION MANAGEMENT
    # =============================================================================

    def initialize(
        self,
        login: int = 0,
        password: str = "",
        server: str = "",
        path: str = "",
        timeout: int = 60000,
        portable: bool = False
    ) -> bool:
        """
        Initialize connection to MT5 terminal.

        This method initializes the MT5 terminal connection. If credentials are
        provided, it will also attempt to log in to the trading account.

        Args:
            login: Account login number
            password: Account password
            server: MT5 server name
            path: Path to MT5 terminal (overrides instance path if provided)
            timeout: Connection timeout in milliseconds
            portable: Use portable mode

        Returns:
            bool: True if initialization successful, False otherwise

        Example:
            >>> client = MT5Client()
            >>> success = client.initialize(
            ...     login=12345,
            ...     password="mypassword",
            ...     server="Broker-Demo"
            ... )
            >>> if success:
            ...     print("Initialized successfully")
        """
        logger.info("Initializing MT5 terminal connection")
        self.connection_state = ConnectionState.INITIALIZING
        self._connection_attempts += 1

        try:
            # Update instance attributes if provided
            if path is not None:
                self.path = path
            if timeout is not None:
                self.timeout = timeout
            if portable is not None:
                self.portable = portable

            # Initialize MT5 terminal
            if self.path:
                if not mt5.initialize(
                    path=self.path,
                    timeout=self.timeout,
                    portable=self.portable
                ):
                    error = mt5.last_error()
                    self._handle_error(error)
                    logger.error(f"MT5 initialization failed: {error}")
                    self.connection_state = ConnectionState.FAILED
                    self._failed_connections += 1
                    return False
            else:
                if not mt5.initialize(timeout=self.timeout, portable=self.portable):
                    error = mt5.last_error()
                    self._handle_error(error)
                    logger.error(f"MT5 initialization failed: {error}")
                    self.connection_state = ConnectionState.FAILED
                    self._failed_connections += 1
                    return False

            logger.success("MT5 terminal initialized")

            # If credentials provided, attempt login
            if login and password and server:
                if not self.login(login, password, server):
                    logger.warning("Initialization successful but login failed")
                    return False

            self.connection_state = ConnectionState.CONNECTED
            self._successful_connections += 1
            self._last_connection_time = datetime.now()

            # Trigger connect event
            self.trigger_event('connect', client=self)

            logger.success("MT5 client initialized and connected successfully")
            return True

        except Exception as e:
            logger.error(f"Exception during initialization: {e}")
            self.connection_state = ConnectionState.FAILED
            self._failed_connections += 1
            self._handle_error((0, str(e)))
            return False

    def connect(
        self,
        login: int = 0,
        password: str = "",
        server: str = "",
        path: str = "",
    ) -> bool:
        """
        Connect to MT5 terminal (alias for initialize with login).

        Args:
            login: Account login number
            password: Account password
            server: MT5 server name

        Returns:
            bool: True if connection successful, False otherwise

        Example:
            >>> client = MT5Client()
            >>> client.connect(login=12345, password="pass", server="Demo")
        """
        return self.initialize(login=login, password=password, server=server, path=path)

    def disconnect(self) -> bool:
        """
        Disconnect from MT5 terminal.

        Returns:
            bool: True if disconnection successful

        Example:
            >>> client.disconnect()
        """
        logger.info("Disconnecting from MT5 terminal")

        try:
            self.connection_state = ConnectionState.DISCONNECTED

            # Trigger disconnect event
            self.trigger_event('disconnect', client=self)

            logger.success("Disconnected from MT5 terminal")
            return True

        except Exception as e:
            logger.error(f"Error during disconnection: {e}")
            return False

    def shutdown(self) -> None:
        """
        Shutdown the MT5 terminal connection and clean up resources.

        This method should be called when you're done using the client to
        properly close the connection and release resources.

        Example:
            >>> client = MT5Client()
            >>> client.initialize()
            >>> # ... do work ...
            >>> client.shutdown()
        """
        logger.info("Shutting down MT5 client")

        try:
            # Disconnect first
            self.disconnect()

            # Shutdown MT5 terminal
            mt5.shutdown()

            self.connection_state = ConnectionState.DISCONNECTED
            logger.success("MT5 client shutdown successfully")

        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

    def is_connected(self) -> bool:
        """
        Check if client is currently connected to MT5 terminal.

        Returns:
            bool: True if connected, False otherwise

        Example:
            >>> if client.is_connected():
            ...     print("Currently connected")
        """
        # Check both our state and MT5's terminal info
        terminal_info = mt5.terminal_info()
        is_mt5_connected = terminal_info is not None and terminal_info.connected

        is_our_state_connected = self.connection_state == ConnectionState.CONNECTED

        # Update our state if there's a mismatch
        if is_our_state_connected and not is_mt5_connected:
            logger.warning("Connection state mismatch detected - updating state")
            self.connection_state = ConnectionState.DISCONNECTED

            # Attempt auto-reconnection if enabled
            if self.auto_reconnect_enabled and not self._reconnection_in_progress:
                logger.info("Initiating auto-reconnection")
                self._handle_reconnection()

        return is_mt5_connected and is_our_state_connected

    def ping(self) -> bool:
        """
        Ping the MT5 terminal to check connection health.

        Returns:
            bool: True if ping successful (connected and responsive)

        Example:
            >>> if client.ping():
            ...     print("Connection is healthy")
        """
        try:
            terminal_info = mt5.terminal_info()
            if terminal_info is not None:
                logger.debug("Ping successful")
                return True
            else:
                logger.warning("Ping failed - no terminal info")
                return False
        except Exception as e:
            logger.error(f"Ping failed with exception: {e}")
            return False

    # =============================================================================
    # AUTHENTICATION
    # =============================================================================

    def login(
        self,
        login: int,
        password: str,
        server: str
    ) -> bool:
        """
        Log in to a trading account.

        Args:
            login: Account login number
            password: Account password
            server: MT5 server name

        Returns:
            bool: True if login successful, False otherwise

        Example:
            >>> client = MT5Client()
            >>> client.initialize()
            >>> client.login(12345, "mypassword", "Broker-Demo")
        """
        logger.info(f"Attempting login to account {login} on server {server}")

        try:
            # Attempt authorization
            authorized = mt5.login(login=login, password=password, server=server)

            if authorized:
                self.account_login = login
                self.account_password = password
                self.account_server = server
                self.connection_state = ConnectionState.CONNECTED

                logger.success(f"Successfully logged in to account {login}")
                return True
            else:
                error = mt5.last_error()
                self._handle_error(error)
                logger.error(f"Login failed: {error}")
                return False

        except Exception as e:
            logger.error(f"Exception during login: {e}")
            self._handle_error((0, str(e)))
            return False

    def logout(self) -> bool:
        """
        Log out from the current trading account.

        Returns:
            bool: True if logout successful

        Example:
            >>> client.logout()
        """
        logger.info("Logging out from trading account")

        try:
            self.account_login = None
            self.account_password = None
            self.account_server = None

            logger.success("Logged out successfully")
            return True

        except Exception as e:
            logger.error(f"Error during logout: {e}")
            return False

    # =============================================================================
    # AUTO-RECONNECTION
    # =============================================================================

    def reconnect(self) -> bool:
        """
        Attempt to reconnect to MT5 terminal.

        Uses stored credentials to reconnect. If no credentials are stored,
        returns False.

        Returns:
            bool: True if reconnection successful, False otherwise

        Example:
            >>> if not client.is_connected():
            ...     client.reconnect()
        """
        logger.info("Attempting reconnection to MT5 terminal")
        self.connection_state = ConnectionState.RECONNECTING

        if not (self.account_login and self.account_password and self.account_server):
            logger.error("Cannot reconnect: no credentials stored")
            return False

        # Shutdown existing connection
        try:
            mt5.shutdown()
        except:
            pass

        # Wait a moment before reconnecting
        time.sleep(1)

        # Attempt to reinitialize and login
        success = self.initialize(
            login=self.account_login,
            password=self.account_password,
            server=self.account_server,
            path=self.path,
            timeout=self.timeout,
            portable=self.portable
        )

        if success:
            logger.success("Reconnection successful")
            self.trigger_event('reconnect', client=self)
        else:
            logger.error("Reconnection failed")
            self.connection_state = ConnectionState.FAILED

        return success

    def enable_auto_reconnect(self, retry_attempts: int = 3, retry_delay: int = 5) -> None:
        """
        Enable automatic reconnection on connection loss.

        Args:
            retry_attempts: Number of reconnection attempts (default: 3)
            retry_delay: Delay between attempts in seconds (default: 5)

        Example:
            >>> client.enable_auto_reconnect(retry_attempts=5, retry_delay=10)
        """
        self.auto_reconnect_enabled = True
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        logger.info(
            f"Auto-reconnection enabled: {retry_attempts} attempts, "
            f"{retry_delay}s delay"
        )

    def disable_auto_reconnect(self) -> None:
        """
        Disable automatic reconnection.

        Example:
            >>> client.disable_auto_reconnect()
        """
        self.auto_reconnect_enabled = False
        logger.info("Auto-reconnection disabled")

    def set_retry_attempts(self, attempts: int) -> None:
        """
        Set the number of reconnection retry attempts.

        Args:
            attempts: Number of retry attempts

        Example:
            >>> client.set_retry_attempts(5)
        """
        self.retry_attempts = attempts
        logger.info(f"Retry attempts set to {attempts}")

    def set_retry_delay(self, delay: int) -> None:
        """
        Set the delay between reconnection attempts.

        Args:
            delay: Delay in seconds

        Example:
            >>> client.set_retry_delay(10)
        """
        self.retry_delay = delay
        logger.info(f"Retry delay set to {delay} seconds")

    def _handle_reconnection(self) -> bool:
        """
        Internal method to handle automatic reconnection logic.

        Returns:
            bool: True if reconnection successful
        """
        if self._reconnection_in_progress:
            return False

        self._reconnection_in_progress = True
        logger.info("Starting auto-reconnection process")

        for attempt in range(1, self.retry_attempts + 1):
            logger.info(f"Reconnection attempt {attempt}/{self.retry_attempts}")

            if self.reconnect():
                self._reconnection_in_progress = False
                logger.success("Auto-reconnection successful")
                return True

            if attempt < self.retry_attempts:
                logger.info(f"Waiting {self.retry_delay} seconds before next attempt")
                time.sleep(self.retry_delay)

        self._reconnection_in_progress = False
        logger.error("Auto-reconnection failed after all attempts")
        return False

    # =============================================================================
    # CONFIGURATION MANAGEMENT
    # =============================================================================

    def configure(self, **kwargs) -> None:
        """
        Configure client settings.

        Accepts any key-value pairs to update client configuration.

        Args:
            **kwargs: Configuration parameters

        Example:
            >>> client.configure(
            ...     auto_reconnect=True,
            ...     retry_attempts=5,
            ...     retry_delay=10
            ... )
        """
        logger.info(f"Updating configuration with {len(kwargs)} parameters")

        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
                logger.debug(f"Set {key} = {value}")
            else:
                self.config[key] = value
                logger.debug(f"Added custom config {key} = {value}")

        logger.success("Configuration updated successfully")

    def get_config(self, key: Optional[str] = None) -> Any:
        """
        Get configuration value(s).

        Args:
            key: Configuration key (if None, returns all config)

        Returns:
            Configuration value or dict of all configuration

        Example:
            >>> retry_attempts = client.get_config('retry_attempts')
            >>> all_config = client.get_config()
        """
        if key is None:
            # Return all configuration
            config_dict = {
                'path': self.path,
                'timeout': self.timeout,
                'portable': self.portable,
                'auto_reconnect_enabled': self.auto_reconnect_enabled,
                'retry_attempts': self.retry_attempts,
                'retry_delay': self.retry_delay,
                **self.config
            }
            return config_dict
        else:
            # Return specific config value
            if hasattr(self, key):
                return getattr(self, key)
            else:
                return self.config.get(key)

    def load_config(self, filepath: str) -> bool:
        """
        Load configuration from a JSON file.

        Args:
            filepath: Path to configuration JSON file

        Returns:
            bool: True if loaded successfully

        Example:
            >>> client.load_config('config.json')
        """
        logger.info(f"Loading configuration from {filepath}")

        try:
            with open(filepath, 'r') as f:
                config = json.load(f)

            self.configure(**config)
            self.config_path = filepath

            logger.success(f"Configuration loaded from {filepath}")
            return True

        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            return False

    def save_config(self, filepath: Optional[str] = None) -> bool:
        """
        Save current configuration to a JSON file.

        Args:
            filepath: Path to save configuration (uses stored path if None)

        Returns:
            bool: True if saved successfully

        Example:
            >>> client.save_config('config.json')
        """
        if filepath is None:
            filepath = self.config_path

        if filepath is None:
            logger.error("No filepath provided and no stored config path")
            return False

        logger.info(f"Saving configuration to {filepath}")

        try:
            config = self.get_config()

            # Remove non-serializable items
            config_to_save = {
                k: v for k, v in config.items()
                if isinstance(v, (str, int, float, bool, list, dict, type(None)))
            }

            # Don't save sensitive data
            config_to_save.pop('password', None)

            with open(filepath, 'w') as f:
                json.dump(config_to_save, f, indent=4)

            self.config_path = filepath
            logger.success(f"Configuration saved to {filepath}")
            return True

        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            return False

    # =============================================================================
    # MULTI-ACCOUNT SUPPORT
    # =============================================================================

    def switch_account(
        self,
        account_name: str,
        login: Optional[int] = None,
        password: Optional[str] = None,
        server: Optional[str] = None
    ) -> bool:
        """
        Switch to a different trading account.

        Args:
            account_name: Name identifier for the account
            login: Account login number (required if account not saved)
            password: Account password (required if account not saved)
            server: MT5 server name (required if account not saved)

        Returns:
            bool: True if switch successful

        Example:
            >>> # Switch to saved account
            >>> client.switch_account('demo_account')
            >>>
            >>> # Switch to new account
            >>> client.switch_account(
            ...     'live_account',
            ...     login=54321,
            ...     password='password',
            ...     server='Broker-Live'
            ... )
        """
        logger.info(f"Switching to account: {account_name}")

        # Check if account is saved
        if account_name in self.accounts:
            account_info = self.accounts[account_name]
            login = account_info['login']
            password = account_info['password']
            server = account_info['server']
            logger.info(f"Using saved credentials for {account_name}")
        elif not (login and password and server):
            logger.error(f"Account {account_name} not found and credentials not provided")
            return False

        # Attempt login
        if self.login(login, password, server):
            self.current_account = account_name

            # Save account if not already saved
            if account_name not in self.accounts:
                self.save_account(account_name, login, password, server)

            # Trigger account switch event
            self.trigger_event('account_switch', client=self, account=account_name)

            logger.success(f"Switched to account: {account_name}")
            return True
        else:
            logger.error(f"Failed to switch to account: {account_name}")
            return False

    def save_account(
        self,
        account_name: str,
        login: int,
        password: str,
        server: str,
        path: str
    ) -> None:
        """
        Save account credentials for quick switching.

        Args:
            account_name: Name identifier for the account
            login: Account login number
            password: Account password
            server: MT5 server name
            path: Path to MT5 terminal executable
        Example:
            >>> client.save_account('demo', 12345, 'pass', 'Demo-Server', 'C:/Program Files/MT5/terminal64.exe')
        """
        self.accounts[account_name] = {
            'login': login,
            'password': password,
            'server': server,
            'path': path,
            'saved_at': datetime.now().isoformat()
        }
        logger.success(f"Account '{account_name}' saved")

    def load_account(self, filepath: str) -> bool:
        """
        Load saved accounts from a JSON file.

        Args:
            filepath: Path to accounts JSON file

        Returns:
            bool: True if loaded successfully

        Example:
            >>> client.load_account('accounts.json')
        """
        logger.info(f"Loading accounts from {filepath}")

        try:
            with open(filepath, 'r') as f:
                accounts = json.load(f)

            self.accounts.update(accounts)
            logger.success(f"Loaded {len(accounts)} accounts from {filepath}")
            return True

        except Exception as e:
            logger.error(f"Failed to load accounts: {e}")
            return False

    def list_accounts(self) -> List[str]:
        """
        List all saved account names.

        Returns:
            List of account names

        Example:
            >>> accounts = client.list_accounts()
            >>> print(accounts)
            ['demo_account', 'live_account']
        """
        return list(self.accounts.keys())

    def remove_account(self, account_name: str) -> bool:
        """
        Remove a saved account.

        Args:
            account_name: Name of account to remove

        Returns:
            bool: True if removed successfully

        Example:
            >>> client.remove_account('old_demo')
        """
        if account_name in self.accounts:
            del self.accounts[account_name]
            logger.success(f"Account '{account_name}' removed")
            return True
        else:
            logger.warning(f"Account '{account_name}' not found")
            return False

    # =============================================================================
    # EVENT SYSTEM
    # =============================================================================

    def on(self, event: str, callback: Callable) -> None:
        """
        Register an event callback.

        Available events: 'connect', 'disconnect', 'error', 'reconnect', 'account_switch'

        Args:
            event: Event name
            callback: Callback function to execute when event occurs

        Example:
            >>> def on_connect(client):
            ...     print(f"Connected: {client}")
            >>>
            >>> client.on('connect', on_connect)
        """
        if event not in self._event_handlers:
            self._event_handlers[event] = []

        self._event_handlers[event].append(callback)
        logger.debug(f"Registered callback for '{event}' event")

    def off(self, event: str, callback: Optional[Callable] = None) -> None:
        """
        Unregister an event callback.

        Args:
            event: Event name
            callback: Specific callback to remove (removes all if None)

        Example:
            >>> client.off('connect', on_connect)  # Remove specific callback
            >>> client.off('connect')  # Remove all callbacks for event
        """
        if event in self._event_handlers:
            if callback is None:
                # Remove all callbacks for this event
                self._event_handlers[event] = []
                logger.debug(f"Removed all callbacks for '{event}' event")
            else:
                # Remove specific callback
                if callback in self._event_handlers[event]:
                    self._event_handlers[event].remove(callback)
                    logger.debug(f"Removed callback for '{event}' event")

    def trigger_event(self, event: str, **kwargs) -> None:
        """
        Trigger an event and execute all registered callbacks.

        Args:
            event: Event name
            **kwargs: Arguments to pass to callbacks

        Example:
            >>> client.trigger_event('connect', client=client)
        """
        if event in self._event_handlers:
            for callback in self._event_handlers[event]:
                try:
                    callback(**kwargs)
                except Exception as e:
                    logger.error(f"Error executing callback for '{event}': {e}")

    # =============================================================================
    # STATUS & DIAGNOSTICS
    # =============================================================================

    def get_status(self) -> Dict[str, Any]:
        """
        Get comprehensive client status information.

        Returns:
            Dictionary containing status information

        Example:
            >>> status = client.get_status()
            >>> print(status['connection_state'])
            >>> print(status['account_info'])
        """
        return {
            'connection_state': str(self.connection_state),
            'is_connected': self.is_connected(),
            'account_info': {
                'login': self.account_login,
                'server': self.account_server,
                'current_account': self.current_account
            },
            'auto_reconnect': {
                'enabled': self.auto_reconnect_enabled,
                'retry_attempts': self.retry_attempts,
                'retry_delay': self.retry_delay
            },
            'terminal_info': mt5.terminal_info()._asdict() if mt5.terminal_info() else None,
            'statistics': self.get_connection_statistics()
        }

    def get_connection_statistics(self) -> Dict[str, Any]:
        """
        Get connection statistics and metrics.

        Returns:
            Dictionary containing connection statistics

        Example:
            >>> stats = client.get_connection_statistics()
            >>> print(f"Success rate: {stats['success_rate']:.2%}")
        """
        total_attempts = self._connection_attempts
        success_rate = (
            self._successful_connections / total_attempts
            if total_attempts > 0 else 0
        )

        return {
            'total_attempts': total_attempts,
            'successful_connections': self._successful_connections,
            'failed_connections': self._failed_connections,
            'success_rate': success_rate,
            'last_connection_time': (
                self._last_connection_time.isoformat()
                if self._last_connection_time else None
            ),
            'error_count': self._error_count,
            'last_error': self._last_error
        }

    # =============================================================================
    # ERROR HANDLING
    # =============================================================================

    def get_error(self) -> Optional[Tuple[int, str]]:
        """
        Get the last error that occurred.

        Returns:
            Tuple of (error_code, error_description) or None

        Example:
            >>> error = client.get_error()
            >>> if error:
            ...     print(f"Error {error[0]}: {error[1]}")
        """
        return self._last_error

    def handle_error(self, error_code: int, error_message: str) -> None:
        """
        Handle an error (public interface for error handling).

        Args:
            error_code: Error code
            error_message: Error message

        Example:
            >>> client.handle_error(10004, "Connection failed")
        """
        self._handle_error((error_code, error_message))

    def _handle_error(self, error: Tuple[int, str]) -> None:
        """
        Internal error handling method.

        Args:
            error: Tuple of (error_code, error_description)
        """
        self._last_error = error
        self._error_count += 1

        # Trigger error event
        self.trigger_event('error', client=self, error=error)

        logger.error(f"Error {error[0]}: {error[1]}")

    # =============================================================================
    # UTILITY METHODS
    # =============================================================================

    def reset(self) -> None:
        """
        Reset client to initial state.

        This clears all statistics, errors, and disconnects from MT5.

        Example:
            >>> client.reset()
        """
        logger.info("Resetting MT5 client")

        # Shutdown connection
        self.shutdown()

        # Reset connection statistics
        self._connection_attempts = 0
        self._successful_connections = 0
        self._failed_connections = 0
        self._last_connection_time = None
        self._total_connection_time = 0

        # Reset error tracking
        self._last_error = None
        self._error_count = 0

        # Reset authentication
        self.account_login = None
        self.account_password = None
        self.account_server = None

        # Reset state
        self.connection_state = ConnectionState.DISCONNECTED
        self._reconnection_in_progress = False

        logger.success("MT5 client reset complete")

    def export_logs(self, filepath: str, include_mt5_logs: bool = False) -> bool:
        """
        Export client logs and statistics to a file.

        Args:
            filepath: Path to save log file
            include_mt5_logs: Whether to include MT5 terminal logs

        Returns:
            bool: True if export successful

        Example:
            >>> client.export_logs('client_logs.json')
        """
        logger.info(f"Exporting logs to {filepath}")

        try:
            log_data = {
                'timestamp': datetime.now().isoformat(),
                'client_status': self.get_status(),
                'statistics': self.get_connection_statistics(),
                'configuration': self.get_config(),
                'saved_accounts': list(self.accounts.keys()),
            }

            with open(filepath, 'w') as f:
                json.dump(log_data, f, indent=4, default=str)

            logger.success(f"Logs exported to {filepath}")
            return True

        except Exception as e:
            logger.error(f"Failed to export logs: {e}")
            return False

    def __repr__(self) -> str:
        """Return string representation of the client."""
        return (
            f"MT5Client(state={self.connection_state}, "
            f"account={self.account_login}, server={self.account_server})"
        )

    def __str__(self) -> str:
        """Return user-friendly string representation."""
        return f"MT5Client [{self.connection_state}]"

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures proper cleanup."""
        self.shutdown()


# Export the client class
__all__ = ['MT5Client']
