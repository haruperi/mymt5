"""MT5Terminal - Terminal information and diagnostics"""

from mylogger import logger
from typing import Optional, Dict, Any, Union
import MetaTrader5 as mt5
from datetime import datetime
import platform
import sys


class MT5Terminal:
    """
    MT5Terminal class for managing terminal information and diagnostics.

    This class provides methods to retrieve terminal information, check terminal status,
    get terminal properties, and perform compatibility checks.
    """

    def __init__(self, client):
        """
        Initialize MT5Terminal with a client instance.

        Args:
            client: MT5Client instance for MT5 operations
        """
        logger.info("Initializing MT5Terminal")
        self.client = client
        self._terminal_info_cache = None
        self._cache_timestamp = None
        self._cache_duration = 5  # seconds

    # ============================================================
    # 1. Terminal Information
    # ============================================================

    def get(self, attribute: Optional[str] = None) -> Union[Any, Dict[str, Any]]:
        """
        Unified getter for terminal information.

        Args:
            attribute: Specific attribute to get (e.g., 'build', 'name', 'path', etc.)
                      If None, returns all terminal information as dict

        Returns:
            Requested attribute value or complete terminal info dict

        Raises:
            ValueError: If attribute doesn't exist
            RuntimeError: If failed to retrieve terminal info

        Examples:
            >>> terminal.get('build')
            3730
            >>> terminal.get('name')
            'MetaTrader 5'
            >>> terminal.get()  # Returns all info
            {'build': 3730, 'name': 'MetaTrader 5', ...}
        """
        logger.info(f"Getting terminal info: attribute={attribute}")

        terminal_info = self._fetch_terminal_info()

        if attribute is None:
            return terminal_info

        if attribute not in terminal_info:
            logger.error(f"Invalid attribute: {attribute}")
            raise ValueError(f"Attribute '{attribute}' does not exist")

        return terminal_info[attribute]

    def _fetch_terminal_info(self) -> Dict[str, Any]:
        """
        Private method to fetch terminal information from MT5.
        Implements caching to reduce API calls.

        Returns:
            Dictionary with terminal information

        Raises:
            RuntimeError: If failed to retrieve terminal info
        """
        # Check cache
        if self._terminal_info_cache is not None and self._cache_timestamp is not None:
            elapsed = (datetime.now() - self._cache_timestamp).total_seconds()
            if elapsed < self._cache_duration:
                logger.debug("Returning cached terminal info")
                return self._terminal_info_cache

        logger.debug("Fetching fresh terminal info from MT5")
        terminal_info = mt5.terminal_info()

        if terminal_info is None:
            error_code, error_desc = mt5.last_error()
            logger.error(f"Failed to get terminal info: {error_code} - {error_desc}")
            raise RuntimeError(f"Failed to get terminal info: {error_code} - {error_desc}")

        # Convert to dictionary
        info_dict = {
            'community_account': terminal_info.community_account,
            'community_connection': terminal_info.community_connection,
            'connected': terminal_info.connected,
            'dlls_allowed': terminal_info.dlls_allowed,
            'trade_allowed': terminal_info.trade_allowed,
            'tradeapi_disabled': terminal_info.tradeapi_disabled,
            'email_enabled': terminal_info.email_enabled,
            'ftp_enabled': terminal_info.ftp_enabled,
            'notifications_enabled': terminal_info.notifications_enabled,
            'mqid': terminal_info.mqid,
            'build': terminal_info.build,
            'maxbars': terminal_info.maxbars,
            'codepage': terminal_info.codepage,
            'ping_last': terminal_info.ping_last,
            'community_balance': terminal_info.community_balance,
            'retransmission': terminal_info.retransmission,
            'company': terminal_info.company,
            'name': terminal_info.name,
            'language': terminal_info.language,
            'path': terminal_info.path,
            'data_path': terminal_info.data_path,
            'commondata_path': terminal_info.commondata_path,
        }

        # Update cache
        self._terminal_info_cache = info_dict
        self._cache_timestamp = datetime.now()

        logger.info("Terminal info retrieved successfully")
        return info_dict

    # ============================================================
    # 2. Terminal Status
    # ============================================================

    def check(self, status_type: str) -> bool:
        """
        Check terminal status.

        Args:
            status_type: Type of status to check:
                - 'connected': Is terminal connected to server?
                - 'trade_allowed': Is trading allowed in terminal?
                - 'dlls_allowed': Are DLLs allowed?
                - 'email_enabled': Is email notification enabled?
                - 'ftp_enabled': Is FTP enabled?
                - 'notifications_enabled': Are push notifications enabled?
                - 'community_connection': Connected to MQL5 community?
                - 'tradeapi_disabled': Is trade API disabled?

        Returns:
            Boolean status result

        Raises:
            ValueError: If status_type is invalid

        Examples:
            >>> terminal.check('connected')
            True
            >>> terminal.check('trade_allowed')
            True
        """
        logger.info(f"Checking terminal status: {status_type}")

        valid_types = [
            'connected', 'trade_allowed', 'dlls_allowed', 'email_enabled',
            'ftp_enabled', 'notifications_enabled', 'community_connection',
            'tradeapi_disabled'
        ]
        if status_type not in valid_types:
            logger.error(f"Invalid status_type: {status_type}")
            raise ValueError(f"Invalid status_type. Must be one of {valid_types}")

        terminal_info = self._fetch_terminal_info()
        result = terminal_info[status_type]

        logger.info(f"Status check {status_type}: {result}")
        return result

    # ============================================================
    # 3. Terminal Properties
    # ============================================================

    def get_properties(self, property_type: str = 'all') -> Dict[str, Any]:
        """
        Get terminal properties grouped by type.

        Args:
            property_type: Type of properties to get:
                - 'resources': CPU, memory, and performance metrics
                - 'display': Display and UI settings
                - 'limits': Terminal limits and restrictions
                - 'all': All properties

        Returns:
            Dictionary with requested properties

        Raises:
            ValueError: If property_type is invalid

        Examples:
            >>> terminal.get_properties('resources')
            {'maxbars': 100000, 'ping_last': 45, ...}
            >>> terminal.get_properties('all')
            {'resources': {...}, 'display': {...}, 'limits': {...}}
        """
        logger.info(f"Getting terminal properties: property_type={property_type}")

        valid_types = ['resources', 'display', 'limits', 'all']
        if property_type not in valid_types:
            logger.error(f"Invalid property_type: {property_type}")
            raise ValueError(f"Invalid property_type. Must be one of {valid_types}")

        if property_type == 'resources':
            return self._get_resources()
        elif property_type == 'display':
            return self._get_display_info()
        elif property_type == 'limits':
            return self._get_limits()
        elif property_type == 'all':
            return {
                'resources': self._get_resources(),
                'display': self._get_display_info(),
                'limits': self._get_limits()
            }

    def _get_resources(self) -> Dict[str, Any]:
        """
        Get terminal resource information.

        Returns:
            Dictionary with resource metrics
        """
        logger.debug("Getting terminal resources")
        terminal_info = self._fetch_terminal_info()

        resources = {
            'maxbars': terminal_info['maxbars'],
            'ping_last': terminal_info['ping_last'],
            'retransmission': terminal_info['retransmission'],
            'community_balance': terminal_info['community_balance'],
        }

        return resources

    def _get_display_info(self) -> Dict[str, Any]:
        """
        Get terminal display information.

        Returns:
            Dictionary with display settings
        """
        logger.debug("Getting terminal display info")
        terminal_info = self._fetch_terminal_info()

        display = {
            'name': terminal_info['name'],
            'company': terminal_info['company'],
            'language': terminal_info['language'],
            'build': terminal_info['build'],
            'codepage': terminal_info['codepage'],
        }

        return display

    def _get_limits(self) -> Dict[str, Any]:
        """
        Get terminal limits and restrictions.

        Returns:
            Dictionary with terminal limits
        """
        logger.debug("Getting terminal limits")
        terminal_info = self._fetch_terminal_info()

        limits = {
            'dlls_allowed': terminal_info['dlls_allowed'],
            'trade_allowed': terminal_info['trade_allowed'],
            'tradeapi_disabled': terminal_info['tradeapi_disabled'],
            'maxbars': terminal_info['maxbars'],
        }

        return limits

    # ============================================================
    # 4. Utility Methods
    # ============================================================

    def get_summary(self) -> Dict[str, Any]:
        """
        Get terminal summary with key information.

        Returns:
            Dictionary with terminal summary
        """
        logger.info("Getting terminal summary")

        terminal_info = self._fetch_terminal_info()

        summary = {
            'name': terminal_info['name'],
            'company': terminal_info['company'],
            'build': terminal_info['build'],
            'language': terminal_info['language'],
            'connected': terminal_info['connected'],
            'trade_allowed': terminal_info['trade_allowed'],
            'path': terminal_info['path'],
            'data_path': terminal_info['data_path'],
            'maxbars': terminal_info['maxbars'],
            'ping_last': terminal_info['ping_last'],
            'dlls_allowed': terminal_info['dlls_allowed'],
            'tradeapi_disabled': terminal_info['tradeapi_disabled'],
            'email_enabled': terminal_info['email_enabled'],
            'notifications_enabled': terminal_info['notifications_enabled'],
        }

        logger.info("Terminal summary generated")
        return summary

    def print_info(self):
        """
        Print formatted terminal information to console.
        """
        logger.info("Printing terminal info")

        terminal_info = self._fetch_terminal_info()

        print("\n" + "="*60)
        print("MT5 TERMINAL INFORMATION")
        print("="*60)
        print(f"\nBasic Information:")
        print(f"  Name:        {terminal_info['name']}")
        print(f"  Company:     {terminal_info['company']}")
        print(f"  Build:       {terminal_info['build']}")
        print(f"  Language:    {terminal_info['language']}")
        print(f"\nPaths:")
        print(f"  Terminal:    {terminal_info['path']}")
        print(f"  Data:        {terminal_info['data_path']}")
        print(f"  Common Data: {terminal_info['commondata_path']}")
        print(f"\nConnection Status:")
        print(f"  Connected:   {terminal_info['connected']}")
        print(f"  Ping:        {terminal_info['ping_last']} ms")
        print(f"\nTrading Status:")
        print(f"  Trade Allowed:     {terminal_info['trade_allowed']}")
        print(f"  DLLs Allowed:      {terminal_info['dlls_allowed']}")
        print(f"  Trade API:         {'Disabled' if terminal_info['tradeapi_disabled'] else 'Enabled'}")
        print(f"\nNotifications:")
        print(f"  Email:             {terminal_info['email_enabled']}")
        print(f"  Push:              {terminal_info['notifications_enabled']}")
        print(f"  FTP:               {terminal_info['ftp_enabled']}")
        print(f"\nCommunity:")
        print(f"  Connected:   {terminal_info['community_connection']}")
        print(f"  Account:     {terminal_info['community_account']}")
        print(f"  Balance:     {terminal_info['community_balance']}")
        print(f"\nLimits:")
        print(f"  Max Bars:    {terminal_info['maxbars']}")
        print(f"  Code Page:   {terminal_info['codepage']}")
        print("="*60 + "\n")

    def export(self, format: str = 'dict', filepath: Optional[str] = None) -> Union[Dict, str]:
        """
        Export terminal information.

        Args:
            format: Export format ('dict', 'json', 'csv')
            filepath: Optional file path to save export

        Returns:
            Exported data as dict or JSON string

        Examples:
            >>> terminal.export('dict')
            {...}
            >>> terminal.export('json', 'terminal_info.json')
            'Exported to terminal_info.json'
        """
        logger.info(f"Exporting terminal info: format={format}")

        terminal_info = self._fetch_terminal_info()

        if format == 'dict':
            return terminal_info
        elif format == 'json':
            import json
            json_str = json.dumps(terminal_info, indent=2, default=str)

            if filepath:
                with open(filepath, 'w') as f:
                    f.write(json_str)
                logger.info(f"Terminal info exported to {filepath}")
                return f"Exported to {filepath}"
            return json_str
        elif format == 'csv':
            import csv

            if not filepath:
                filepath = 'terminal_info.csv'

            with open(filepath, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Field', 'Value'])
                for key, value in terminal_info.items():
                    writer.writerow([key, value])

            logger.info(f"Terminal info exported to {filepath}")
            return f"Exported to {filepath}"
        else:
            logger.error(f"Invalid export format: {format}")
            raise ValueError(f"Invalid format. Must be 'dict', 'json', or 'csv'")

    def check_compatibility(self) -> Dict[str, Any]:
        """
        Check system compatibility with MT5.

        Returns:
            Dictionary with compatibility information
        """
        logger.info("Checking system compatibility")

        terminal_info = self._fetch_terminal_info()

        # Get Python information
        python_version = sys.version
        python_version_info = sys.version_info

        # Get system information
        system_info = {
            'platform': platform.system(),
            'platform_release': platform.release(),
            'platform_version': platform.version(),
            'architecture': platform.machine(),
            'processor': platform.processor(),
        }

        # Check MT5 version
        mt5_version_info = mt5.version()

        compatibility = {
            'python': {
                'version': python_version,
                'major': python_version_info.major,
                'minor': python_version_info.minor,
                'micro': python_version_info.micro,
                'compatible': python_version_info.major == 3 and python_version_info.minor >= 8
            },
            'system': system_info,
            'mt5': {
                'version': mt5_version_info,
                'build': terminal_info['build'],
                'name': terminal_info['name'],
                'company': terminal_info['company']
            },
            'terminal': {
                'connected': terminal_info['connected'],
                'trade_allowed': terminal_info['trade_allowed'],
                'dlls_allowed': terminal_info['dlls_allowed'],
                'tradeapi_disabled': terminal_info['tradeapi_disabled']
            },
            'overall_status': self._assess_compatibility(
                python_version_info, terminal_info, system_info
            )
        }

        logger.info(f"Compatibility check complete: {compatibility['overall_status']}")
        return compatibility

    def _assess_compatibility(self, python_version_info, terminal_info, system_info) -> str:
        """
        Assess overall compatibility status.

        Args:
            python_version_info: Python version information
            terminal_info: Terminal information
            system_info: System information

        Returns:
            Compatibility status string
        """
        issues = []

        # Check Python version
        if not (python_version_info.major == 3 and python_version_info.minor >= 8):
            issues.append("Python version should be 3.8 or higher")

        # Check terminal connection
        if not terminal_info['connected']:
            issues.append("Terminal not connected to server")

        # Check trade API
        if terminal_info['tradeapi_disabled']:
            issues.append("Trade API is disabled")

        # Check trading permission
        if not terminal_info['trade_allowed']:
            issues.append("Trading not allowed in terminal")

        # Check platform
        if system_info['platform'] not in ['Windows', 'Linux', 'Darwin']:
            issues.append(f"Platform '{system_info['platform']}' may not be fully supported")

        if len(issues) == 0:
            return "Compatible - No issues detected"
        elif len(issues) == 1:
            return f"Warning - 1 issue: {issues[0]}"
        else:
            return f"Warning - {len(issues)} issues detected"


logger.info("MT5Terminal module loaded")
