"""
Example 12: Simple Backtesting Framework

This example demonstrates how to backtest a trading strategy using historical data
from MT5. It includes a simple moving average crossover strategy as an example.
"""

from mymt5 import MT5Client, MT5Data, MT5Symbol, MT5Utils
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import configparser


# ==================== BACKTEST FRAMEWORK ====================

class Backtest:
    """Simple backtesting framework for MT5 strategies"""
    
    def __init__(self, initial_balance=10000.0, risk_per_trade=0.01, commission=0.0001):
        """
        Initialize backtest
        
        Args:
            initial_balance: Starting account balance
            risk_per_trade: Risk per trade as fraction of balance (0.01 = 1%)
            commission: Commission per trade (0.0001 = 1 pip)
        """
        self.initial_balance = initial_balance
        self.risk_per_trade = risk_per_trade
        self.commission = commission
        
        # Track results
        self.balance = initial_balance
        self.equity = initial_balance
        self.trades = []
        self.positions = []
        
    def open_position(self, entry_time, entry_price, direction, stop_loss, take_profit, lot_size):
        """Open a position"""
        position = {
            'entry_time': entry_time,
            'entry_price': entry_price,
            'direction': direction,  # 'long' or 'short'
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'lot_size': lot_size,
            'open': True
        }
        self.positions.append(position)
        return len(self.positions) - 1  # Return position index
    
    def close_position(self, position_idx, exit_time, exit_price):
        """Close a position and record trade"""
        position = self.positions[position_idx]
        
        if not position['open']:
            return  # Already closed
        
        # Calculate profit/loss
        if position['direction'] == 'long':
            price_diff = exit_price - position['entry_price']
        else:  # short
            price_diff = position['entry_price'] - exit_price
        
        # Calculate profit in account currency (assuming 1 pip = $10 for standard lot)
        pip_value = 10  # $10 per pip for 1 standard lot
        profit = price_diff * 10000 * position['lot_size'] * pip_value  # Convert to pips
        
        # Subtract commission
        commission_cost = self.commission * 10000 * position['lot_size'] * pip_value * 2  # Entry + exit
        profit -= commission_cost
        
        # Update balance
        self.balance += profit
        
        # Record trade
        trade = {
            'entry_time': position['entry_time'],
            'exit_time': exit_time,
            'entry_price': position['entry_price'],
            'exit_price': exit_price,
            'direction': position['direction'],
            'lot_size': position['lot_size'],
            'profit': profit,
            'balance': self.balance
        }
        self.trades.append(trade)
        
        # Mark position as closed
        position['open'] = False
        position['exit_time'] = exit_time
        position['exit_price'] = exit_price
        position['profit'] = profit
    
    def check_stops(self, current_time, high, low):
        """Check if any positions hit stop loss or take profit"""
        for idx, position in enumerate(self.positions):
            if not position['open']:
                continue
            
            if position['direction'] == 'long':
                # Check stop loss
                if low <= position['stop_loss']:
                    self.close_position(idx, current_time, position['stop_loss'])
                # Check take profit
                elif high >= position['take_profit']:
                    self.close_position(idx, current_time, position['take_profit'])
            else:  # short
                # Check stop loss
                if high >= position['stop_loss']:
                    self.close_position(idx, current_time, position['stop_loss'])
                # Check take profit
                elif low <= position['take_profit']:
                    self.close_position(idx, current_time, position['take_profit'])
    
    def close_all_positions(self, exit_time, exit_price):
        """Close all open positions"""
        for idx, position in enumerate(self.positions):
            if position['open']:
                self.close_position(idx, exit_time, exit_price)
    
    def get_results(self):
        """Calculate and return backtest results"""
        if not self.trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'total_profit': 0,
                'final_balance': self.balance,
                'return_pct': 0,
                'profit_factor': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'largest_win': 0,
                'largest_loss': 0
            }
        
        # Convert trades to DataFrame
        trades_df = pd.DataFrame(self.trades)
        
        # Calculate metrics
        winning_trades = trades_df[trades_df['profit'] > 0]
        losing_trades = trades_df[trades_df['profit'] < 0]
        
        total_profit = trades_df['profit'].sum()
        gross_profit = winning_trades['profit'].sum() if len(winning_trades) > 0 else 0
        gross_loss = abs(losing_trades['profit'].sum()) if len(losing_trades) > 0 else 0
        
        results = {
            'total_trades': len(self.trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': (len(winning_trades) / len(self.trades)) * 100,
            'total_profit': total_profit,
            'final_balance': self.balance,
            'return_pct': ((self.balance - self.initial_balance) / self.initial_balance) * 100,
            'profit_factor': gross_profit / gross_loss if gross_loss > 0 else 0,
            'avg_win': winning_trades['profit'].mean() if len(winning_trades) > 0 else 0,
            'avg_loss': losing_trades['profit'].mean() if len(losing_trades) > 0 else 0,
            'largest_win': winning_trades['profit'].max() if len(winning_trades) > 0 else 0,
            'largest_loss': losing_trades['profit'].min() if len(losing_trades) > 0 else 0,
            'trades_df': trades_df
        }
        
        return results
    
    def print_results(self):
        """Print formatted backtest results"""
        results = self.get_results()
        
        print("\n" + "="*60)
        print("BACKTEST RESULTS")
        print("="*60)
        print(f"Initial Balance:    ${self.initial_balance:,.2f}")
        print(f"Final Balance:      ${results['final_balance']:,.2f}")
        print(f"Total Profit:       ${results['total_profit']:,.2f}")
        print(f"Return:             {results['return_pct']:.2f}%")
        print("-"*60)
        print(f"Total Trades:       {results['total_trades']}")
        print(f"Winning Trades:     {results['winning_trades']}")
        print(f"Losing Trades:      {results['losing_trades']}")
        print(f"Win Rate:           {results['win_rate']:.2f}%")
        print("-"*60)
        print(f"Profit Factor:      {results['profit_factor']:.2f}")
        print(f"Average Win:        ${results['avg_win']:,.2f}")
        print(f"Average Loss:       ${results['avg_loss']:,.2f}")
        print(f"Largest Win:        ${results['largest_win']:,.2f}")
        print(f"Largest Loss:       ${results['largest_loss']:,.2f}")
        print("="*60)


# ==================== STRATEGY EXAMPLE: MA CROSSOVER ====================

class MACrossoverStrategy:
    """Simple Moving Average Crossover Strategy"""
    
    def __init__(self, fast_period=20, slow_period=50):
        """
        Initialize strategy
        
        Args:
            fast_period: Fast MA period
            slow_period: Slow MA period
        """
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.position = None  # Current position direction
    
    def calculate_indicators(self, data):
        """Calculate technical indicators"""
        data['fast_ma'] = data['close'].rolling(window=self.fast_period).mean()
        data['slow_ma'] = data['close'].rolling(window=self.slow_period).mean()
        return data
    
    def generate_signals(self, data):
        """Generate trading signals"""
        data = self.calculate_indicators(data)
        
        signals = []
        
        for i in range(len(data)):
            if i < self.slow_period:
                signals.append(None)
                continue
            
            current_fast = data['fast_ma'].iloc[i]
            current_slow = data['slow_ma'].iloc[i]
            prev_fast = data['fast_ma'].iloc[i-1]
            prev_slow = data['slow_ma'].iloc[i-1]
            
            # Bullish crossover
            if prev_fast <= prev_slow and current_fast > current_slow:
                if self.position != 'long':
                    signals.append('buy')
                    self.position = 'long'
                else:
                    signals.append(None)
            # Bearish crossover
            elif prev_fast >= prev_slow and current_fast < current_slow:
                if self.position != 'short':
                    signals.append('sell')
                    self.position = 'short'
                else:
                    signals.append(None)
            else:
                signals.append(None)
        
        data['signal'] = signals
        return data


# ==================== RUN BACKTEST ====================

def run_backtest():
    """Run a simple backtest"""
    
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║                  SIMPLE BACKTESTING                      ║
    ║                                                          ║
    ║  Strategy: Moving Average Crossover                      ║
    ║  • Fast MA: 20 periods                                   ║
    ║  • Slow MA: 50 periods                                   ║
    ║  • Entry: On MA crossover                                ║
    ║  • Exit: On opposite crossover                           ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    # Load configuration
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    # Initialize MT5 client
    client = MT5Client()
    client.initialize(
        login=int(config['MT5']['login']),
        password=config['MT5']['password'],
        server=config['MT5']['server']
    )
    
    if not client.is_connected():
        print("Failed to connect to MT5")
        return
    
    print("✓ Connected to MT5")
    
    # Initialize data manager
    data_manager = MT5Data(client)
    symbol_manager = MT5Symbol(client)
    
    # Get historical data
    symbol = 'EURUSD'
    timeframe = 'H1'
    
    print(f"\nFetching historical data for {symbol} {timeframe}...")
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)  # 3 months of data
    
    bars = data_manager.get_bars(
        symbol=symbol,
        timeframe=timeframe,
        start_date=start_date,
        end_date=end_date
    )
    
    if bars is None or bars.empty:
        print("Failed to get historical data")
        client.shutdown()
        return
    
    print(f"✓ Retrieved {len(bars)} bars")
    
    # Get symbol info for calculations
    symbol_info = symbol_manager.get_info(symbol)
    
    # Initialize backtest
    backtest = Backtest(
        initial_balance=10000.0,
        risk_per_trade=0.01,
        commission=0.0001
    )
    
    # Initialize strategy
    strategy = MACrossoverStrategy(fast_period=20, slow_period=50)
    
    # Generate signals
    print("\nGenerating trading signals...")
    bars = strategy.generate_signals(bars)
    
    # Run backtest
    print("Running backtest...")
    
    current_position_idx = None
    
    for i in range(len(bars)):
        row = bars.iloc[i]
        
        # Check stops for open positions
        if current_position_idx is not None:
            backtest.check_stops(row.name, row['high'], row['low'])
            
            # Check if position was closed
            if not backtest.positions[current_position_idx]['open']:
                current_position_idx = None
        
        # Process signals
        signal = row['signal']
        
        if signal == 'buy':
            # Close short if open
            if current_position_idx is not None:
                backtest.close_position(current_position_idx, row.name, row['close'])
            
            # Open long
            stop_loss = row['close'] - 0.0050  # 50 pips SL
            take_profit = row['close'] + 0.0100  # 100 pips TP
            lot_size = 0.01  # Mini lot
            
            current_position_idx = backtest.open_position(
                entry_time=row.name,
                entry_price=row['close'],
                direction='long',
                stop_loss=stop_loss,
                take_profit=take_profit,
                lot_size=lot_size
            )
        
        elif signal == 'sell':
            # Close long if open
            if current_position_idx is not None:
                backtest.close_position(current_position_idx, row.name, row['close'])
            
            # Open short
            stop_loss = row['close'] + 0.0050  # 50 pips SL
            take_profit = row['close'] - 0.0100  # 100 pips TP
            lot_size = 0.01  # Mini lot
            
            current_position_idx = backtest.open_position(
                entry_time=row.name,
                entry_price=row['close'],
                direction='short',
                stop_loss=stop_loss,
                take_profit=take_profit,
                lot_size=lot_size
            )
    
    # Close any remaining positions
    if current_position_idx is not None and backtest.positions[current_position_idx]['open']:
        backtest.close_position(
            current_position_idx,
            bars.index[-1],
            bars['close'].iloc[-1]
        )
    
    # Print results
    backtest.print_results()
    
    # Save trades to file
    results = backtest.get_results()
    if 'trades_df' in results:
        trades_df = results['trades_df']
        trades_df.to_csv('backtest_trades.csv', index=False)
        print(f"\n✓ Trades saved to 'backtest_trades.csv'")
    
    # Plot equity curve (optional, requires matplotlib)
    try:
        import matplotlib.pyplot as plt
        
        trades_df = results['trades_df']
        
        plt.figure(figsize=(12, 6))
        plt.plot(trades_df.index, trades_df['balance'])
        plt.axhline(y=backtest.initial_balance, color='r', linestyle='--', label='Initial Balance')
        plt.title('Equity Curve')
        plt.xlabel('Trade Number')
        plt.ylabel('Balance ($)')
        plt.legend()
        plt.grid(True)
        plt.savefig('equity_curve.png')
        print("✓ Equity curve saved to 'equity_curve.png'")
        
    except ImportError:
        print("\nNote: Install matplotlib to generate equity curve plot")
        print("  pip install matplotlib")
    
    # Cleanup
    client.shutdown()
    print("\n✓ Backtest complete!")


# ==================== MAIN ====================

if __name__ == '__main__':
    try:
        run_backtest()
    except KeyboardInterrupt:
        print("\n\nBacktest interrupted by user")
    except Exception as e:
        print(f"\n⚠️  Error: {e}")
        import traceback
        traceback.print_exc()

