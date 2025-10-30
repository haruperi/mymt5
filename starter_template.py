"""
MyMT5 Starter Template

This is a basic template for creating your own MT5 trading bot.
Copy this file and customize it for your needs.

Usage:
    1. Copy config.ini.example to config.ini
    2. Fill in your MT5 credentials in config.ini
    3. Customize the strategy logic below
    4. Run: python starter_template.py
"""

import sys
import time
import logging
import configparser
from datetime import datetime
from typing import Optional, Dict, Any

# Import MyMT5 components
from mymt5 import (
    MT5Client,
    MT5Account,
    MT5Symbol,
    MT5Data,
    MT5Trade,
    MT5Risk,
    MT5History,
    MT5Validator
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class TradingBot:
    """Basic trading bot template"""
    
    def __init__(self, config_file='config.ini'):
        """Initialize the trading bot"""
        logger.info("Initializing Trading Bot...")
        
        # Load configuration
        self.config = self.load_config(config_file)
        
        # Initialize MT5 client
        self.client = MT5Client()
        self.connected = False
        
        # Initialize component managers (will be set after connection)
        self.account = None
        self.symbol_manager = None
        self.data_manager = None
        self.trade_manager = None
        self.risk_manager = None
        self.history_manager = None
        self.validator = None
        
        # Bot state
        self.running = False
        self.symbols = self.config['STRATEGY']['symbols'].split(',')
        self.timeframe = self.config['STRATEGY']['timeframe']
        
    def load_config(self, config_file):
        """Load configuration from file"""
        config = configparser.ConfigParser()
        config.read(config_file)
        
        if not config.sections():
            raise ValueError(f"Config file '{config_file}' not found or empty")
        
        return config
    
    def connect(self):
        """Connect to MT5"""
        logger.info("Connecting to MT5...")
        
        try:
            success = self.client.initialize(
                login=int(self.config['MT5']['login']),
                password=self.config['MT5']['password'],
                server=self.config['MT5']['server']
            )
            
            if success:
                self.connected = True
                logger.info("✓ Connected to MT5")
                
                # Initialize managers
                self.account = MT5Account(self.client)
                self.symbol_manager = MT5Symbol(self.client)
                self.data_manager = MT5Data(self.client)
                self.trade_manager = MT5Trade(self.client, symbol_manager=self.symbol_manager)
                self.risk_manager = MT5Risk(self.client, account_manager=self.account)
                self.history_manager = MT5History(self.client)
                self.validator = MT5Validator(self.client)
                
                # Initialize symbols
                for symbol in self.symbols:
                    self.symbol_manager.initialize(symbol.strip())
                
                # Set up risk limits
                self.setup_risk_limits()
                
                return True
            else:
                error = self.client.get_error()
                logger.error(f"✗ Connection failed: {error}")
                return False
                
        except Exception as e:
            logger.error(f"✗ Connection error: {e}", exc_info=True)
            return False
    
    def setup_risk_limits(self):
        """Set up risk management limits"""
        logger.info("Setting up risk limits...")
        
        self.risk_manager.set_limit(
            'max_risk_per_trade',
            float(self.config['RISK']['max_risk_per_trade'])
        )
        self.risk_manager.set_limit(
            'max_daily_loss',
            float(self.config['RISK']['max_daily_loss'])
        )
        self.risk_manager.set_limit(
            'max_positions',
            int(self.config['RISK']['max_positions'])
        )
        
        logger.info("✓ Risk limits configured")
    
    def check_account_health(self):
        """Check if account is healthy for trading"""
        try:
            health = self.account.calculate('health')
            
            if health['status'] != 'healthy':
                logger.warning(f"Account health: {health['status']}")
                logger.warning(f"Margin level: {health['margin_level']}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking account health: {e}")
            return False
    
    def get_market_data(self, symbol, count=100):
        """Get market data for a symbol"""
        try:
            bars = self.data_manager.get_bars(
                symbol=symbol,
                timeframe=self.timeframe,
                count=count
            )
            return bars
        except Exception as e:
            logger.error(f"Error getting market data for {symbol}: {e}")
            return None
    
    def analyze_market(self, symbol, bars):
        """
        Analyze market data and generate trading signals
        
        TODO: Implement your trading strategy here!
        
        Args:
            symbol: Symbol name
            bars: Historical bars DataFrame
        
        Returns:
            dict: Signal dict with 'action', 'entry', 'sl', 'tp', or None
        """
        # Example: Simple moving average crossover
        # Replace this with your own strategy!
        
        if bars is None or len(bars) < 50:
            return None
        
        # Calculate indicators
        bars['sma_20'] = bars['close'].rolling(window=20).mean()
        bars['sma_50'] = bars['close'].rolling(window=50).mean()
        
        # Get latest values
        current_price = bars['close'].iloc[-1]
        sma_20_current = bars['sma_20'].iloc[-1]
        sma_50_current = bars['sma_50'].iloc[-1]
        sma_20_prev = bars['sma_20'].iloc[-2]
        sma_50_prev = bars['sma_50'].iloc[-2]
        
        # Generate signals
        # Bullish crossover
        if sma_20_prev <= sma_50_prev and sma_20_current > sma_50_current:
            return {
                'action': 'buy',
                'entry': current_price,
                'sl': current_price - 0.0050,  # 50 pips
                'tp': current_price + 0.0100,  # 100 pips
            }
        
        # Bearish crossover
        elif sma_20_prev >= sma_50_prev and sma_20_current < sma_50_current:
            return {
                'action': 'sell',
                'entry': current_price,
                'sl': current_price + 0.0050,  # 50 pips
                'tp': current_price - 0.0100,  # 100 pips
            }
        
        return None
    
    def execute_signal(self, symbol, signal):
        """Execute a trading signal"""
        try:
            logger.info(f"Executing {signal['action']} signal for {symbol}")
            
            # Calculate position size with risk management
            size = self.risk_manager.calculate_size(
                symbol=symbol,
                method='percent',
                risk_percent=float(self.config['RISK']['default_risk_percent']),
                entry_price=signal['entry'],
                stop_loss=signal['sl']
            )
            
            # Execute trade
            if signal['action'] == 'buy':
                result = self.trade_manager.buy(
                    symbol=symbol,
                    volume=size['volume'],
                    stop_loss=signal['sl'],
                    take_profit=signal['tp'],
                    comment=self.config['TRADING']['default_comment']
                )
            else:  # sell
                result = self.trade_manager.sell(
                    symbol=symbol,
                    volume=size['volume'],
                    stop_loss=signal['sl'],
                    take_profit=signal['tp'],
                    comment=self.config['TRADING']['default_comment']
                )
            
            if result['success']:
                logger.info(f"✓ Trade executed: Order {result['order']}")
            else:
                logger.error(f"✗ Trade failed: {result['error']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing signal: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}
    
    def manage_positions(self):
        """Manage open positions"""
        try:
            positions = self.trade_manager.get_positions()
            
            for position in positions:
                # Add your position management logic here
                # Example: Trailing stop, break-even, partial closes, etc.
                pass
            
        except Exception as e:
            logger.error(f"Error managing positions: {e}")
    
    def run(self):
        """Main bot loop"""
        logger.info("="*60)
        logger.info("STARTING TRADING BOT")
        logger.info("="*60)
        
        # Connect to MT5
        if not self.connect():
            logger.error("Failed to connect to MT5")
            return
        
        # Display account info
        balance = self.account.get('balance')
        equity = self.account.get('equity')
        logger.info(f"Account Balance: ${balance:,.2f}")
        logger.info(f"Account Equity: ${equity:,.2f}")
        
        self.running = True
        iteration = 0
        
        try:
            while self.running:
                iteration += 1
                logger.info(f"\n{'='*60}")
                logger.info(f"Iteration {iteration} - {datetime.now()}")
                logger.info(f"{'='*60}")
                
                # Check account health
                if not self.check_account_health():
                    logger.warning("Account health check failed, waiting...")
                    time.sleep(60)
                    continue
                
                # Process each symbol
                for symbol in self.symbols:
                    logger.info(f"\nProcessing {symbol}...")
                    
                    # Get market data
                    bars = self.get_market_data(symbol)
                    
                    if bars is None:
                        continue
                    
                    # Analyze market
                    signal = self.analyze_market(symbol, bars)
                    
                    if signal:
                        logger.info(f"Signal generated: {signal['action']} {symbol}")
                        
                        # Execute signal
                        self.execute_signal(symbol, signal)
                    
                    # Manage existing positions
                    self.manage_positions()
                
                # Wait before next iteration
                logger.info(f"\nWaiting 60 seconds...")
                time.sleep(60)
                
        except KeyboardInterrupt:
            logger.info("\n\nBot stopped by user")
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Clean shutdown"""
        logger.info("\n" + "="*60)
        logger.info("SHUTTING DOWN")
        logger.info("="*60)
        
        if self.connected:
            # Optional: Close all positions
            # positions = self.trade_manager.get_positions()
            # for position in positions:
            #     self.trade_manager.close_position(ticket=position['ticket'])
            
            # Disconnect
            self.client.shutdown()
            logger.info("✓ Disconnected from MT5")
        
        logger.info("="*60)
        logger.info("BOT STOPPED")
        logger.info("="*60)


def main():
    """Main entry point"""
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║                   MYMT5 TRADING BOT                      ║
    ║                                                          ║
    ║  This is a starter template. Customize the strategy     ║
    ║  logic in the analyze_market() method.                  ║
    ║                                                          ║
    ║  Press Ctrl+C to stop the bot                           ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    try:
        # Create and run bot
        bot = TradingBot()
        bot.run()
    except Exception as e:
        logger.critical(f"Critical error: {e}", exc_info=True)
        print(f"\n⚠️  Critical error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

