from mylogger import logger
"""
MT5Trade Usage Examples

This example demonstrates comprehensive usage of the MT5Trade class for:
- Executing market and pending orders
- Managing orders (modify, cancel)
- Managing positions (modify, close, reverse)
- Analyzing positions
- Trade validation
"""

from mymt5.client import MT5Client
from mymt5.trade import MT5Trade
from mymt5.enums import OrderType
import time


def example1_market_orders():
    """Example 1: Executing market orders."""
    print("\n" + "="*60)
    print("Example 1: Market Orders")
    print("="*60)

    client = MT5Client()
    client.initialize()
    client.connect_from_config()

    trade = MT5Trade(client=client)

    # Simple market buy
    print("\n1. Market Buy Order:")
    result = trade.buy("EURUSD", 0.01, sl=1.0500, tp=1.1000)
    if result:
        print(f"✓ Order executed: Deal={result['deal']}, Order={result['order']}")
        print(f"  Price: {result['price']:.5f}")
    else:
        print("✗ Order failed")

    # Simple market sell
    print("\n2. Market Sell Order:")
    result = trade.sell("EURUSD", 0.01, sl=1.1500, tp=1.1000)
    if result:
        print(f"✓ Order executed: Deal={result['deal']}, Order={result['order']}")
    else:
        print("✗ Order failed")

    client.disconnect()


def example2_pending_orders():
    """Example 2: Pending orders."""
    print("\n" + "="*60)
    print("Example 2: Pending Orders")
    print("="*60)

    client = MT5Client()
    client.initialize()
    client.connect_from_config()

    trade = MT5Trade(client=client)

    # Buy limit order
    print("\n1. Buy Limit Order:")
    result = trade.execute(
        symbol="EURUSD",
        order_type=OrderType.BUY_LIMIT,
        volume=0.01,
        price=1.0900,  # Below current price
        sl=1.0850,
        tp=1.0950
    )
    if result:
        print(f"✓ Pending order placed: Order={result['order']}")
    else:
        print("✗ Order failed")

    # Sell stop order
    print("\n2. Sell Stop Order:")
    result = trade.execute(
        symbol="EURUSD",
        order_type=OrderType.SELL_STOP,
        volume=0.01,
        price=1.0850,  # Below current price
        sl=1.0900,
        tp=1.0800
    )
    if result:
        print(f"✓ Pending order placed: Order={result['order']}")
    else:
        print("✗ Order failed")

    client.disconnect()


def example3_order_management():
    """Example 3: Managing orders."""
    print("\n" + "="*60)
    print("Example 3: Order Management")
    print("="*60)

    client = MT5Client()
    client.initialize()
    client.connect_from_config()

    trade = MT5Trade(client=client)

    # Get all open orders
    print("\n1. Retrieving Open Orders:")
    orders = trade.get_orders()
    if orders is not None and len(orders) > 0:
        print(f"✓ Found {len(orders)} open orders:")
        for _, order in orders.head().iterrows():
            print(f"  - Order {order['ticket']}: {order['symbol']} {order['type']} {order['volume']}")
    else:
        print("  No open orders")

    # Modify an order (if exists)
    if orders is not None and len(orders) > 0:
        order_ticket = orders.iloc[0]['ticket']
        print(f"\n2. Modifying Order {order_ticket}:")
        result = trade.modify_order(order_ticket, sl=1.0800, tp=1.1000)
        if result:
            print(f"✓ Order modified successfully")
        else:
            print("✗ Modification failed")

        # Cancel the order
        print(f"\n3. Cancelling Order {order_ticket}:")
        result = trade.cancel_order(ticket=order_ticket)
        if result:
            print(f"✓ Order cancelled successfully")
        else:
            print("✗ Cancellation failed")

    client.disconnect()


def example4_position_management():
    """Example 4: Managing positions."""
    print("\n" + "="*60)
    print("Example 4: Position Management")
    print("="*60)

    client = MT5Client()
    client.initialize()
    client.connect_from_config()

    trade = MT5Trade(client=client)

    # Get all open positions
    print("\n1. Retrieving Open Positions:")
    positions = trade.get_positions()
    if positions is not None and len(positions) > 0:
        print(f"✓ Found {len(positions)} open positions:")
        for _, pos in positions.head().iterrows():
            pos_type = "BUY" if pos['type'] == 0 else "SELL"
            print(f"  - Position {pos['ticket']}: {pos['symbol']} {pos_type} {pos['volume']} | "
                  f"Profit: ${pos['profit']:.2f}")
    else:
        print("  No open positions")

    # Modify position (if exists)
    if positions is not None and len(positions) > 0:
        pos_symbol = positions.iloc[0]['symbol']
        print(f"\n2. Modifying Position SL/TP for {pos_symbol}:")
        result = trade.modify_position(pos_symbol, sl=1.0900, tp=1.1100)
        if result:
            print(f"✓ Position modified successfully")
        else:
            print("✗ Modification failed")

        # Partially close position
        pos_volume = positions.iloc[0]['volume']
        if pos_volume >= 0.02:
            print(f"\n3. Partially Closing Position (50%):")
            result = trade.close_position(symbol=pos_symbol, volume=pos_volume/2)
            if result:
                print(f"✓ Position partially closed")
            else:
                print("✗ Partial close failed")

    client.disconnect()


def example5_position_analytics():
    """Example 5: Position analytics."""
    print("\n" + "="*60)
    print("Example 5: Position Analytics")
    print("="*60)

    client = MT5Client()
    client.initialize()
    client.connect_from_config()

    trade = MT5Trade(client=client)

    # Get positions
    positions = trade.get_positions()

    if positions is not None and len(positions) > 0:
        print(f"\nAnalyzing {len(positions)} open positions:\n")

        for _, pos in positions.iterrows():
            print(f"Position {pos['ticket']} - {pos['symbol']}:")
            print("-" * 40)

            # Get all metrics
            metrics = trade.analyze_position(ticket=pos['ticket'], metric='all')
            if metrics:
                print(f"  Type: {metrics['type']}")
                print(f"  Volume: {metrics['volume']}")
                print(f"  Entry Price: {metrics['entry_price']:.5f}")
                print(f"  Current Price: {metrics['current_price']:.5f}")
                print(f"  Profit: ${metrics['profit']:.2f}")
                print(f"  Profit (points): {metrics['profit_points']:.1f}")
                print(f"  Duration: {metrics['duration']/3600:.1f} hours")
                if metrics['sl']:
                    print(f"  Stop Loss: {metrics['sl']:.5f}")
                if metrics['tp']:
                    print(f"  Take Profit: {metrics['tp']:.5f}")
            print()

        # Get overall statistics
        print("\nOverall Position Statistics:")
        print("="*40)
        stats = trade.get_position_stats()
        if stats:
            print(f"Total Positions: {stats['total_positions']}")
            print(f"Total Volume: {stats['total_volume']}")
            print(f"Total Profit: ${stats['total_profit']:.2f}")
            print(f"Buy Positions: {stats['buy_positions']}")
            print(f"Sell Positions: {stats['sell_positions']}")
            print(f"Profitable: {stats['profitable_positions']}")
            print(f"Losing: {stats['losing_positions']}")
            print(f"Symbols: {', '.join(stats['symbols'])}")
    else:
        print("\nNo open positions to analyze")

    client.disconnect()


def example6_reverse_position():
    """Example 6: Reversing a position."""
    print("\n" + "="*60)
    print("Example 6: Position Reversal")
    print("="*60)

    client = MT5Client()
    client.initialize()
    client.connect_from_config()

    trade = MT5Trade(client=client)

    # Get first position
    positions = trade.get_positions()

    if positions is not None and len(positions) > 0:
        pos = positions.iloc[0]
        pos_type = "BUY" if pos['type'] == 0 else "SELL"

        print(f"\nCurrent Position:")
        print(f"  Symbol: {pos['symbol']}")
        print(f"  Type: {pos_type}")
        print(f"  Volume: {pos['volume']}")
        print(f"  Profit: ${pos['profit']:.2f}")

        # Reverse it
        print(f"\nReversing position...")
        result = trade.reverse_position(pos['symbol'], ticket=pos['ticket'])

        if result:
            print(f"✓ Position reversed successfully!")
            print(f"  New position opened")
        else:
            print("✗ Position reversal failed")
    else:
        print("\nNo positions to reverse")

    client.disconnect()


def example7_batch_operations():
    """Example 7: Batch operations."""
    print("\n" + "="*60)
    print("Example 7: Batch Operations")
    print("="*60)

    client = MT5Client()
    client.initialize()
    client.connect_from_config()

    trade = MT5Trade(client=client)

    # Cancel all orders for a symbol
    print("\n1. Cancelling All EURUSD Orders:")
    results = trade.cancel_order(symbol="EURUSD")
    if isinstance(results, list):
        print(f"✓ Cancelled {len(results)} orders")
    else:
        print("  No orders to cancel")

    # Close all positions
    print("\n2. Closing All Positions:")
    results = trade.close_position(close_all=True)
    if isinstance(results, list):
        print(f"✓ Closed {len(results)} positions")
        for i, result in enumerate(results, 1):
            print(f"  {i}. Deal: {result['deal']}, Retcode: {result['retcode']}")
    else:
        print("  No positions to close")

    client.disconnect()


def example8_validation():
    """Example 8: Trade validation."""
    print("\n" + "="*60)
    print("Example 8: Trade Validation")
    print("="*60)

    client = MT5Client()
    client.initialize()
    client.connect_from_config()

    trade = MT5Trade(client=client)

    # Build a request
    print("\n1. Validating Trade Request:")
    request = trade.build_request(
        symbol="EURUSD",
        order_type=OrderType.BUY,
        volume=0.01,
        sl=1.0900,
        tp=1.1100
    )

    if request:
        valid, message = trade.validate_request(request)
        if valid:
            print(f"✓ Request is valid: {message}")
        else:
            print(f"✗ Request validation failed: {message}")

    # Try invalid request
    print("\n2. Validating Invalid Request:")
    invalid_request = {
        'action': 'deal',
        'symbol': 'EURUSD',
        'volume': 0.001,  # Too small
        'type': 0
    }

    valid, message = trade.validate_request(invalid_request)
    if valid:
        print(f"✓ Request is valid")
    else:
        print(f"✗ Request validation failed: {message}")

    # Check order status
    print("\n3. Checking Order Status:")
    order_info = trade.check_order(12345)  # Example ticket
    if order_info:
        print(f"✓ Order found: Status = {order_info['status']}")
    else:
        print("  Order not found (expected)")

    client.disconnect()


def example9_trading_summary():
    """Example 9: Get trading summary."""
    print("\n" + "="*60)
    print("Example 9: Trading Summary")
    print("="*60)

    client = MT5Client()
    client.initialize()
    client.connect_from_config()

    trade = MT5Trade(client=client)

    # Get complete summary
    print("\nTrading Summary:")
    print("="*40)

    summary = trade.get_summary()

    if 'positions' in summary:
        pos_stats = summary['positions']
        print(f"\nPositions:")
        print(f"  Total: {pos_stats.get('total_positions', 0)}")
        if pos_stats.get('total_positions', 0) > 0:
            print(f"  Total Volume: {pos_stats.get('total_volume', 0)}")
            print(f"  Total Profit: ${pos_stats.get('total_profit', 0):.2f}")
            print(f"  Buy: {pos_stats.get('buy_positions', 0)}")
            print(f"  Sell: {pos_stats.get('sell_positions', 0)}")

    if 'orders' in summary:
        ord_stats = summary['orders']
        print(f"\nOrders:")
        print(f"  Total: {ord_stats.get('total_orders', 0)}")
        if ord_stats.get('symbols'):
            print(f"  Symbols: {', '.join(ord_stats.get('symbols', []))}")

    # Export summary
    print("\n\nExporting summary to file...")
    success = trade.export('data/trading_summary.json')
    if success:
        print("✓ Summary exported to data/trading_summary.json")
    else:
        print("✗ Export failed")

    client.disconnect()


def example10_complete_trading_workflow():
    """Example 10: Complete trading workflow."""
    print("\n" + "="*60)
    print("Example 10: Complete Trading Workflow")
    print("="*60)

    client = MT5Client()
    client.initialize()
    client.connect_from_config()

    trade = MT5Trade(client=client)

    print("\n1. Opening Position:")
    print("-" * 40)

    # Execute market buy
    result = trade.buy("EURUSD", 0.01, sl=1.0900, tp=1.1100)

    if result and result['retcode'] == 10009:  # TRADE_RETCODE_DONE
        print(f"✓ Position opened successfully")
        print(f"  Deal: {result['deal']}")
        print(f"  Price: {result['price']:.5f}")

        # Wait a moment
        print("\n2. Waiting 5 seconds...")
        time.sleep(5)

        # Check position
        print("\n3. Checking Position Status:")
        print("-" * 40)
        positions = trade.get_positions(symbol="EURUSD")

        if positions is not None and len(positions) > 0:
            pos = positions.iloc[0]

            # Analyze position
            metrics = trade.analyze_position(ticket=pos['ticket'], metric='all')
            if metrics:
                print(f"  Ticket: {metrics['ticket']}")
                print(f"  Type: {metrics['type']}")
                print(f"  Volume: {metrics['volume']}")
                print(f"  Entry: {metrics['entry_price']:.5f}")
                print(f"  Current: {metrics['current_price']:.5f}")
                print(f"  Profit: ${metrics['profit']:.2f}")
                print(f"  Duration: {metrics['duration']:.0f} seconds")

            # Modify SL/TP
            print("\n4. Modifying Stop Loss and Take Profit:")
            print("-" * 40)
            result = trade.modify_position("EURUSD", sl=1.0950, tp=1.1050)
            if result:
                print("✓ Position modified successfully")

            # Wait a bit more
            print("\n5. Waiting 5 seconds...")
            time.sleep(5)

            # Close position
            print("\n6. Closing Position:")
            print("-" * 40)
            result = trade.close_position(symbol="EURUSD")

            if result and result['retcode'] == 10009:
                print(f"✓ Position closed successfully")
                print(f"  Deal: {result['deal']}")
                print(f"  Price: {result['price']:.5f}")

        print("\n" + "="*60)
        print("Workflow Completed Successfully!")
        print("="*60)

    else:
        print("✗ Failed to open position")
        if result:
            print(f"  Error code: {result['retcode']}")
            print(f"  Message: {result['comment']}")

    client.disconnect()


def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("MT5Trade Usage Examples")
    print("="*60)

    print("\nIMPORTANT: These examples will execute real trades!")
    print("Make sure you're connected to a DEMO account.")
    print("\nPress Enter to continue or Ctrl+C to cancel...")
    input()

    try:
        # Run safer examples first
        example1_market_orders()
        example3_order_management()
        example4_position_management()
        example5_position_analytics()
        example8_validation()
        example9_trading_summary()

        # More advanced examples
        # example2_pending_orders()
        # example6_reverse_position()
        # example7_batch_operations()
        # example10_complete_trading_workflow()

        print("\n" + "="*60)
        print("Examples completed!")
        print("="*60)

    except KeyboardInterrupt:
        print("\n\nExamples cancelled by user")
    except Exception as e:
        logger.error(f"Error running examples: {e}")
        print(f"\nError: {e}")


if __name__ == "__main__":
    main()
