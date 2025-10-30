"""
Example 11: Comprehensive Error Handling

This example demonstrates proper error handling techniques for MyMT5,
including connection errors, trading errors, data retrieval errors, and recovery strategies.
"""

from mymt5 import (
    MT5Client, MT5Account, MT5Symbol, MT5Data, MT5Trade, MT5Validator
)
import logging
import time
from datetime import datetime
import configparser

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('error_handling.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ==================== CONFIGURATION ====================

def load_config(config_file='config.ini'):
    """Load configuration with error handling"""
    try:
        config = configparser.ConfigParser()
        config.read(config_file)
        
        # Validate required sections
        if 'DEMO' not in config:
            raise ValueError("Missing [DEMO] section in config file")
        
        # Validate required keys
        required_keys = ['login', 'password', 'server']
        for key in required_keys:
            if key not in config['DEMO']:
                raise ValueError(f"Missing required key '{key}' in [DEMO] section")
        
        logger.info("Configuration loaded successfully")
        return config
        
    except FileNotFoundError:
        logger.error(f"Config file '{config_file}' not found")
        raise
    except configparser.Error as e:
        logger.error(f"Error parsing config file: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error loading config: {e}")
        raise


# ==================== CONNECTION ERROR HANDLING ====================

def connect_with_retry(client, max_attempts=3, delay=5, **credentials):
    """
    Connect to MT5 with retry logic
    
    Args:
        client: MT5Client instance
        max_attempts: Maximum number of connection attempts
        delay: Delay in seconds between attempts
        **credentials: login, password, server
    
    Returns:
        bool: True if connected, False otherwise
    """
    for attempt in range(1, max_attempts + 1):
        try:
            logger.info(f"Connection attempt {attempt}/{max_attempts}")
            
            success = client.initialize(**credentials)
            
            if success:
                logger.info("✓ Connected successfully")
                return True
            else:
                error = client.get_error()
                logger.warning(f"✗ Connection failed: {error}")
                
                if attempt < max_attempts:
                    logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                    
        except Exception as e:
            logger.error(f"Exception during connection: {e}")
            if attempt < max_attempts:
                logger.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
    
    logger.error("All connection attempts failed")
    return False


def monitor_connection(client, check_interval=10):
    """
    Monitor connection and reconnect if needed
    
    Args:
        client: MT5Client instance
        check_interval: Check interval in seconds
    """
    try:
        while True:
            if not client.is_connected():
                logger.warning("Connection lost! Attempting to reconnect...")
                success = client.reconnect()
                if success:
                    logger.info("✓ Reconnected successfully")
                else:
                    logger.error("✗ Reconnection failed")
            
            time.sleep(check_interval)
            
    except KeyboardInterrupt:
        logger.info("Connection monitoring stopped")


# ==================== TRADING ERROR HANDLING ====================

def execute_trade_safely(trade, **order_params):
    """
    Execute trade with comprehensive error handling
    
    Args:
        trade: MT5Trade instance
        **order_params: Order parameters
    
    Returns:
        dict: Trade result with success status
    """
    try:
        # Validate parameters first
        validator = MT5Validator(trade.client)
        valid, error = validator.validate('trade_request', **order_params)
        
        if not valid:
            logger.error(f"Validation failed: {error}")
            return {
                'success': False,
                'error': f'Validation error: {error}'
            }
        
        # Execute trade
        logger.info(f"Executing trade: {order_params['symbol']} {order_params.get('volume')}")
        
        if order_params.get('order_type') in ['buy', 'BUY']:
            result = trade.buy(**order_params)
        elif order_params.get('order_type') in ['sell', 'SELL']:
            result = trade.sell(**order_params)
        else:
            result = trade.execute(**order_params)
        
        # Check result
        if result.get('success'):
            logger.info(f"✓ Trade successful: Order {result.get('order')}")
        else:
            logger.error(f"✗ Trade failed: {result.get('error')}")
            
            # Handle specific errors
            error_code = result.get('retcode')
            if error_code == 10004:  # TRADE_RETCODE_REQUOTE
                logger.warning("Price changed, retry recommended")
            elif error_code == 10006:  # TRADE_RETCODE_REJECT
                logger.error("Trade rejected by broker")
            elif error_code == 10007:  # TRADE_RETCODE_CANCEL
                logger.warning("Trade canceled by trader")
            elif error_code == 10008:  # TRADE_RETCODE_PLACED
                logger.info("Pending order placed")
            elif error_code == 10013:  # TRADE_RETCODE_INVALID_VOLUME
                logger.error("Invalid volume specified")
            elif error_code == 10014:  # TRADE_RETCODE_INVALID_PRICE
                logger.error("Invalid price specified")
            elif error_code == 10015:  # TRADE_RETCODE_INVALID_STOPS
                logger.error("Invalid stop loss or take profit")
            elif error_code == 10016:  # TRADE_RETCODE_TRADE_DISABLED
                logger.error("Trading is disabled")
            elif error_code == 10018:  # TRADE_RETCODE_MARKET_CLOSED
                logger.error("Market is closed")
            elif error_code == 10019:  # TRADE_RETCODE_NO_MONEY
                logger.error("Insufficient funds")
        
        return result
        
    except Exception as e:
        logger.error(f"Exception during trade execution: {e}", exc_info=True)
        return {
            'success': False,
            'error': f'Exception: {str(e)}'
        }


def close_position_safely(trade, **close_params):
    """
    Close position with error handling
    
    Args:
        trade: MT5Trade instance
        **close_params: Close parameters (ticket, symbol, volume, etc.)
    
    Returns:
        dict: Close result
    """
    try:
        # Get positions first
        if 'ticket' in close_params:
            positions = trade.get_positions(ticket=close_params['ticket'])
            if not positions:
                logger.error(f"Position {close_params['ticket']} not found")
                return {'success': False, 'error': 'Position not found'}
        
        # Attempt to close
        logger.info(f"Closing position: {close_params}")
        result = trade.close_position(**close_params)
        
        if result.get('success'):
            logger.info("✓ Position closed successfully")
        else:
            logger.error(f"✗ Failed to close position: {result.get('error')}")
        
        return result
        
    except Exception as e:
        logger.error(f"Exception while closing position: {e}", exc_info=True)
        return {
            'success': False,
            'error': f'Exception: {str(e)}'
        }


# ==================== DATA RETRIEVAL ERROR HANDLING ====================

def get_data_safely(data_manager, symbol, timeframe, count=100, max_retries=3):
    """
    Get market data with retry logic
    
    Args:
        data_manager: MT5Data instance
        symbol: Symbol name
        timeframe: Timeframe
        count: Number of bars
        max_retries: Maximum number of retries
    
    Returns:
        DataFrame or None
    """
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Fetching data for {symbol} {timeframe} (attempt {attempt}/{max_retries})")
            
            bars = data_manager.get_bars(
                symbol=symbol,
                timeframe=timeframe,
                count=count
            )
            
            if bars is None or bars.empty:
                logger.warning(f"No data returned for {symbol}")
                if attempt < max_retries:
                    time.sleep(2)
                    continue
                return None
            
            logger.info(f"✓ Retrieved {len(bars)} bars")
            return bars
            
        except Exception as e:
            logger.error(f"Exception fetching data: {e}")
            if attempt < max_retries:
                time.sleep(2)
            else:
                logger.error("Max retries reached")
                return None


def get_symbol_info_safely(symbol_manager, symbol):
    """
    Get symbol information with error handling
    
    Args:
        symbol_manager: MT5Symbol instance
        symbol: Symbol name
    
    Returns:
        dict or None
    """
    try:
        # Initialize symbol first
        symbol_manager.initialize(symbol)
        
        # Check if symbol exists
        if not symbol_manager.check(symbol, 'exists'):
            logger.error(f"Symbol '{symbol}' does not exist")
            return None
        
        # Get symbol info
        info = symbol_manager.get_info(symbol)
        logger.info(f"✓ Retrieved info for {symbol}")
        return info
        
    except Exception as e:
        logger.error(f"Exception getting symbol info: {e}", exc_info=True)
        return None


# ==================== ACCOUNT ERROR HANDLING ====================

def check_account_health(account_manager):
    """
    Check account health with error handling
    
    Args:
        account_manager: MT5Account instance
    
    Returns:
        dict: Account health metrics or None
    """
    try:
        # Get account info
        balance = account_manager.get('balance')
        equity = account_manager.get('equity')
        margin_free = account_manager.get('margin_free')
        
        logger.info(f"Account - Balance: ${balance}, Equity: ${equity}")
        
        # Calculate health metrics
        health = account_manager.calculate('health')
        
        if health['status'] != 'healthy':
            logger.warning(f"Account health: {health['status']}")
            logger.warning(f"Margin level: {health['margin_level']}")
        else:
            logger.info("✓ Account is healthy")
        
        return health
        
    except Exception as e:
        logger.error(f"Exception checking account health: {e}", exc_info=True)
        return None


# ==================== COMPREHENSIVE ERROR HANDLING EXAMPLE ====================

def trading_session_with_error_handling():
    """Complete trading session with comprehensive error handling"""
    
    client = None
    
    try:
        # 1. Load configuration
        logger.info("="*50)
        logger.info("STARTING TRADING SESSION")
        logger.info("="*50)
        
        config = load_config()
        
        # 2. Connect with retry logic
        client = MT5Client()
        
        # Enable auto-reconnection
        client.enable_auto_reconnect()
        client.set_retry_attempts(5)
        client.set_retry_delay(3)
        
        # Register event handlers
        def on_connect(c):
            logger.info("EVENT: Connected to MT5")
        
        def on_disconnect(c):
            logger.warning("EVENT: Disconnected from MT5")
        
        client.on('connect', on_connect)
        client.on('disconnect', on_disconnect)
        
        # Connect
        connected = connect_with_retry(
            client,
            max_attempts=3,
            delay=5,
            login=int(config['DEMO']['login']),
            password=config['DEMO']['password'],
            server=config['DEMO']['server'],
            path=config['DEMO']['path']
        )
        
        if not connected:
            logger.error("Failed to connect to MT5")
            return
        
        # 3. Initialize managers
        account = MT5Account(client)
        symbol_manager = MT5Symbol(client)
        data_manager = MT5Data(client)
        trade_manager = MT5Trade(client, symbol_manager=symbol_manager)
        
        # 4. Check account health
        logger.info("\n" + "="*50)
        logger.info("CHECKING ACCOUNT HEALTH")
        logger.info("="*50)
        
        health = check_account_health(account)
        if not health or health['status'] != 'healthy':
            logger.error("Account health check failed")
            return
        
        # 5. Get symbol information
        logger.info("\n" + "="*50)
        logger.info("GETTING SYMBOL INFORMATION")
        logger.info("="*50)
        
        symbol = 'EURUSD'
        symbol_info = get_symbol_info_safely(symbol_manager, symbol)
        if not symbol_info:
            logger.error(f"Failed to get info for {symbol}")
            return
        
        # 6. Get market data
        logger.info("\n" + "="*50)
        logger.info("GETTING MARKET DATA")
        logger.info("="*50)
        
        bars = get_data_safely(data_manager, symbol, 'H1', count=100)
        if bars is None:
            logger.error("Failed to get market data")
            return
        
        # 7. Execute a test trade (commented out for safety)
        logger.info("\n" + "="*50)
        logger.info("TRADE EXECUTION (DRY RUN)")
        logger.info("="*50)
        
        # Get current price
        current_price = symbol_manager.get_price(symbol, 'ask')
        
        # Example trade parameters
        trade_params = {
            'symbol': symbol,
            'volume': 0.01,
            'stop_loss': current_price - 0.0050,  # 50 pips SL
            'take_profit': current_price + 0.0100,  # 100 pips TP
            'comment': 'Error handling example',
            'order_type': 'buy'
        }
        
        logger.info(f"Trade params: {trade_params}")
        logger.info("NOTE: Actual execution is commented out for safety")
        
        # Uncomment to execute real trade:
        # result = execute_trade_safely(trade_manager, **trade_params)
        
        # 8. Monitor for errors
        logger.info("\n" + "="*50)
        logger.info("SESSION RUNNING (Press Ctrl+C to stop)")
        logger.info("="*50)
        
        # Monitor connection and account
        check_count = 0
        while True:
            time.sleep(10)
            check_count += 1
            
            # Check connection
            if not client.is_connected():
                logger.warning("Connection lost during monitoring")
                break
            
            # Periodic account check
            if check_count % 6 == 0:  # Every minute
                health = check_account_health(account)
                if not health or health['status'] != 'healthy':
                    logger.warning("Account health deteriorated")
        
    except KeyboardInterrupt:
        logger.info("\nSession interrupted by user")
        
    except Exception as e:
        logger.error(f"Unexpected error in trading session: {e}", exc_info=True)
        
    finally:
        # Cleanup
        logger.info("\n" + "="*50)
        logger.info("CLEANING UP")
        logger.info("="*50)
        
        if client:
            try:
                # Close any open positions (optional, commented for safety)
                # logger.info("Closing all positions...")
                # positions = trade_manager.get_positions()
                # for position in positions:
                #     close_position_safely(trade_manager, ticket=position['ticket'])
                
                # Disconnect
                logger.info("Disconnecting from MT5...")
                client.shutdown()
                logger.info("✓ Disconnected successfully")
                
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")
        
        logger.info("="*50)
        logger.info("SESSION ENDED")
        logger.info("="*50)


# ==================== MAIN ====================

if __name__ == '__main__':
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║           COMPREHENSIVE ERROR HANDLING EXAMPLE           ║
    ║                                                          ║
    ║  This example demonstrates:                              ║
    ║  • Connection error handling and retry logic             ║
    ║  • Trading error handling and recovery                   ║
    ║  • Data retrieval error handling                         ║
    ║  • Account health monitoring                             ║
    ║  • Event-driven error detection                          ║
    ║  • Comprehensive logging                                 ║
    ║                                                          ║
    ║  Check 'error_handling.log' for detailed logs            ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    try:
        trading_session_with_error_handling()
    except Exception as e:
        logger.critical(f"Critical error: {e}", exc_info=True)
        print(f"\n⚠️  Critical error occurred: {e}")
        print("Check error_handling.log for details")

