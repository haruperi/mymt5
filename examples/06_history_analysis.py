from mylogger import logger
"""
MT5History Usage Examples

This example demonstrates comprehensive usage of the MT5History class for:
- Retrieving historical deals and orders
- Calculating performance metrics
- Analyzing trading patterns
- Generating reports
- Exporting historical data
"""

from mymt5.client import MT5Client
from mymt5.history import MT5History
from datetime import datetime, timedelta
import pandas as pd


def example1_basic_history():
    """Example 1: Basic historical data retrieval."""
    print("\n" + "="*60)
    print("Example 1: Retrieving Historical Data")
    print("="*60)

    # Initialize client and history
    client = MT5Client()
    client.initialize()
    client.connect_from_config()

    history = MT5History(client=client)

    # Get last 30 days of deals
    deals = history.get('deals')
    if deals is not None and len(deals) > 0:
        print(f"\nRetrieved {len(deals)} deals")
        print(f"\nFirst 5 deals:")
        print(deals[['time', 'symbol', 'type', 'volume', 'price', 'profit']].head())
        print(f"\nTotal profit: ${deals['profit'].sum():.2f}")
    else:
        print("\nNo deals found in the last 30 days")

    client.disconnect()


def example2_date_range_history():
    """Example 2: Historical data for specific date range."""
    print("\n" + "="*60)
    print("Example 2: Date Range Historical Data")
    print("="*60)

    client = MT5Client()
    client.initialize()
    client.connect_from_config()

    history = MT5History(client=client)

    # Get deals for January 2024
    start = datetime(2024, 1, 1)
    end = datetime(2024, 1, 31)

    deals = history.get('deals', start=start, end=end)
    if deals is not None and len(deals) > 0:
        print(f"\nRetrieved {len(deals)} deals from {start.date()} to {end.date()}")
        print(f"Total profit/loss: ${deals['profit'].sum():.2f}")
        print(f"Total commission: ${deals['commission'].sum():.2f}")
        print(f"Total swap: ${deals['swap'].sum():.2f}")
    else:
        print(f"\nNo deals found in the specified period")

    client.disconnect()


def example3_filtered_history():
    """Example 3: Filtered historical data."""
    print("\n" + "="*60)
    print("Example 3: Filtered Historical Data")
    print("="*60)

    client = MT5Client()
    client.initialize()
    client.connect_from_config()

    history = MT5History(client=client)

    # Get deals for specific symbol
    deals = history.get('deals', symbol='EURUSD')
    if deals is not None and len(deals) > 0:
        print(f"\nRetrieved {len(deals)} EURUSD deals")
        print(f"Total profit/loss: ${deals['profit'].sum():.2f}")

        # Get orders for the same symbol
        orders = history.get('orders', symbol='EURUSD')
        if orders is not None and len(orders) > 0:
            print(f"\nRetrieved {len(orders)} EURUSD orders")
    else:
        print("\nNo EURUSD deals found")

    client.disconnect()


def example4_quick_access():
    """Example 4: Quick access methods."""
    print("\n" + "="*60)
    print("Example 4: Quick Access Methods")
    print("="*60)

    client = MT5Client()
    client.initialize()
    client.connect_from_config()

    history = MT5History(client=client)

    # Get today's deals
    today_deals = history.get_today('deals')
    if today_deals is not None:
        print(f"\nToday's deals: {len(today_deals)}")
        if len(today_deals) > 0:
            print(f"Today's profit/loss: ${today_deals['profit'].sum():.2f}")

    # Get this week's deals
    week_deals = history.get_period('week', 'deals')
    if week_deals is not None:
        print(f"\nThis week's deals: {len(week_deals)}")
        if len(week_deals) > 0:
            print(f"Week's profit/loss: ${week_deals['profit'].sum():.2f}")

    # Get this month's deals
    month_deals = history.get_period('month', 'deals')
    if month_deals is not None:
        print(f"\nThis month's deals: {len(month_deals)}")
        if len(month_deals) > 0:
            print(f"Month's profit/loss: ${month_deals['profit'].sum():.2f}")

    client.disconnect()


def example5_performance_metrics():
    """Example 5: Calculating performance metrics."""
    print("\n" + "="*60)
    print("Example 5: Performance Metrics")
    print("="*60)

    client = MT5Client()
    client.initialize()
    client.connect_from_config()

    history = MT5History(client=client)

    # Get all metrics at once
    metrics = history.calculate('all')

    if metrics:
        print("\nPerformance Metrics:")
        print(f"{'='*40}")
        print(f"Total Trades: {metrics['total_trades']}")
        print(f"Win Rate: {metrics['win_rate']:.2f}%")
        print(f"Profit Factor: {metrics['profit_factor']:.2f}")
        print(f"Total Profit: ${metrics['total_profit']:.2f}")
        print(f"Average Win: ${metrics['avg_win']:.2f}")
        print(f"Average Loss: ${metrics['avg_loss']:.2f}")
        print(f"Largest Win: ${metrics['largest_win']:.2f}")
        print(f"Largest Loss: ${metrics['largest_loss']:.2f}")
        print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
        print(f"Max Drawdown: ${metrics['max_drawdown']:.2f}")
        print(f"Total Commission: ${metrics['total_commission']:.2f}")
        print(f"Total Swap: ${metrics['total_swap']:.2f}")
    else:
        print("\nNo trading history available for metrics calculation")

    client.disconnect()


def example6_trade_analysis():
    """Example 6: Trade analysis by various dimensions."""
    print("\n" + "="*60)
    print("Example 6: Trade Analysis")
    print("="*60)

    client = MT5Client()
    client.initialize()
    client.connect_from_config()

    history = MT5History(client=client)

    # Analysis by symbol
    print("\n1. Analysis by Symbol:")
    print("-" * 40)
    by_symbol = history.analyze('by_symbol')
    if by_symbol is not None and len(by_symbol) > 0:
        print(by_symbol.to_string(index=False))
    else:
        print("No data available")

    # Analysis by hour of day
    print("\n2. Analysis by Hour:")
    print("-" * 40)
    by_hour = history.analyze('by_hour')
    if by_hour is not None and len(by_hour) > 0:
        print(by_hour.head(10).to_string(index=False))
    else:
        print("No data available")

    # Analysis by weekday
    print("\n3. Analysis by Weekday:")
    print("-" * 40)
    by_weekday = history.analyze('by_weekday')
    if by_weekday is not None and len(by_weekday) > 0:
        print(by_weekday.to_string(index=False))
    else:
        print("No data available")

    client.disconnect()


def example7_winning_losing_trades():
    """Example 7: Analyzing winning and losing trades."""
    print("\n" + "="*60)
    print("Example 7: Winning vs Losing Trades")
    print("="*60)

    client = MT5Client()
    client.initialize()
    client.connect_from_config()

    history = MT5History(client=client)

    # Get winning trades
    winners = history.analyze('winning_trades')
    if winners is not None and len(winners) > 0:
        print("\nWinning Trades:")
        print(f"{'='*40}")
        print(f"Count: {len(winners)}")
        print(f"Total Profit: ${winners['profit'].sum():.2f}")
        print(f"Average Profit: ${winners['profit'].mean():.2f}")
        print(f"Best Trade: ${winners['profit'].max():.2f}")

        # Top 5 winning trades
        print(f"\nTop 5 Winning Trades:")
        top_winners = winners.nlargest(5, 'profit')[['time', 'symbol', 'profit']]
        print(top_winners.to_string(index=False))
    else:
        print("\nNo winning trades found")

    # Get losing trades
    losers = history.analyze('losing_trades')
    if losers is not None and len(losers) > 0:
        print("\n\nLosing Trades:")
        print(f"{'='*40}")
        print(f"Count: {len(losers)}")
        print(f"Total Loss: ${losers['profit'].sum():.2f}")
        print(f"Average Loss: ${losers['profit'].mean():.2f}")
        print(f"Worst Trade: ${losers['profit'].min():.2f}")

        # Top 5 losing trades
        print(f"\nTop 5 Losing Trades:")
        top_losers = losers.nsmallest(5, 'profit')[['time', 'symbol', 'profit']]
        print(top_losers.to_string(index=False))
    else:
        print("\nNo losing trades found")

    client.disconnect()


def example8_report_generation():
    """Example 8: Generating various reports."""
    print("\n" + "="*60)
    print("Example 8: Report Generation")
    print("="*60)

    client = MT5Client()
    client.initialize()
    client.connect_from_config()

    history = MT5History(client=client)

    # Generate summary report
    print("\n1. Summary Report:")
    print("="*40)
    history.print_report('summary')

    # Generate performance report (as dict)
    print("\n2. Performance Report (Dict):")
    print("="*40)
    perf_report = history.generate_report('performance', format='dict')
    if perf_report:
        for key, value in perf_report.items():
            if isinstance(value, float):
                print(f"{key}: {value:.2f}")
            else:
                print(f"{key}: {value}")

    # Generate detailed report
    print("\n3. Detailed Report:")
    print("="*40)
    detailed_report = history.generate_report('detailed', format='dict')
    if detailed_report:
        print("\nMetrics:")
        for key, value in detailed_report['metrics'].items():
            if isinstance(value, float):
                print(f"  {key}: {value:.2f}")

        print("\nTop 3 Symbols by Profit:")
        if detailed_report['by_symbol']:
            for i, symbol_data in enumerate(detailed_report['by_symbol'][:3], 1):
                print(f"  {i}. {symbol_data['symbol']}: ${symbol_data['total_profit']:.2f}")

    client.disconnect()


def example9_export_data():
    """Example 9: Exporting historical data."""
    print("\n" + "="*60)
    print("Example 9: Exporting Historical Data")
    print("="*60)

    client = MT5Client()
    client.initialize()
    client.connect_from_config()

    history = MT5History(client=client)

    # Export deals to CSV
    csv_success = history.export('data/trading_history.csv', 'deals', format='csv')
    print(f"\nCSV export: {'Success' if csv_success else 'Failed'}")

    # Export deals to JSON
    json_success = history.export('data/trading_history.json', 'deals', format='json')
    print(f"JSON export: {'Success' if json_success else 'Failed'}")

    # Export deals to Excel (if openpyxl is installed)
    excel_success = history.export('data/trading_history.xlsx', 'deals', format='excel')
    print(f"Excel export: {'Success' if excel_success else 'Failed (openpyxl not installed)'}")

    client.disconnect()


def example10_comprehensive_analysis():
    """Example 10: Comprehensive trading analysis."""
    print("\n" + "="*60)
    print("Example 10: Comprehensive Trading Analysis")
    print("="*60)

    client = MT5Client()
    client.initialize()
    client.connect_from_config()

    history = MT5History(client=client)

    # Get deals for the last 30 days
    deals = history.get('deals')

    if deals is not None and len(deals) > 0:
        print(f"\nAnalyzing {len(deals)} trades...")

        # 1. Overall performance
        print("\n1. OVERALL PERFORMANCE")
        print("="*60)
        summary = history.get_summary(deals=deals)
        print(f"Trading Period: {summary['date_range']['start'].date()} to {summary['date_range']['end'].date()}")
        print(f"Duration: {summary['date_range']['duration_days']} days")
        print(f"Total Trades: {summary['total_trades']}")
        print(f"Symbols Traded: {summary['symbols_traded']}")
        print(f"Most Traded: {summary['most_traded_symbol']}")
        print(f"Total Profit: ${summary['total_profit']:.2f}")
        print(f"Win Rate: {summary['win_rate']:.2f}%")
        print(f"Profit Factor: {summary['profit_factor']:.2f}")

        # 2. Performance by symbol
        print("\n2. PERFORMANCE BY SYMBOL")
        print("="*60)
        by_symbol = history.analyze('by_symbol', deals=deals)
        if len(by_symbol) > 0:
            print(by_symbol.to_string(index=False))

        # 3. Time-based analysis
        print("\n3. BEST TRADING HOURS")
        print("="*60)
        by_hour = history.analyze('by_hour', deals=deals)
        if len(by_hour) > 0:
            # Top 3 hours
            top_hours = by_hour.nlargest(3, 'total_profit')
            for idx, row in top_hours.iterrows():
                print(f"Hour {int(row['time_unit']):02d}:00 - "
                      f"Trades: {int(row['trades'])}, "
                      f"Profit: ${row['total_profit']:.2f}, "
                      f"Avg: ${row['avg_profit']:.2f}")

        print("\n4. BEST TRADING DAYS")
        print("="*60)
        by_weekday = history.analyze('by_weekday', deals=deals)
        if len(by_weekday) > 0:
            # Sort by profit
            best_days = by_weekday.sort_values('total_profit', ascending=False)
            for idx, row in best_days.iterrows():
                print(f"{row['time_unit']:9s} - "
                      f"Trades: {int(row['trades']):3d}, "
                      f"Profit: ${row['total_profit']:8.2f}, "
                      f"Avg: ${row['avg_profit']:7.2f}")

        # 4. Risk metrics
        print("\n5. RISK METRICS")
        print("="*60)
        metrics = history.calculate('all', deals=deals)
        print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
        print(f"Max Drawdown: ${metrics['max_drawdown']:.2f}")
        print(f"Largest Win: ${metrics['largest_win']:.2f}")
        print(f"Largest Loss: ${metrics['largest_loss']:.2f}")
        print(f"Avg Win/Avg Loss Ratio: {abs(metrics['avg_win']/metrics['avg_loss']):.2f}")

        # 5. Export comprehensive report
        print("\n6. EXPORTING REPORTS")
        print("="*60)
        history.export('data/comprehensive_analysis.csv', 'deals', format='csv')
        history.export('data/comprehensive_analysis.json', 'deals', format='json')
        print("Exported to data/comprehensive_analysis.*")

        print("\n" + "="*60)
        print("Analysis Complete!")
        print("="*60)

    else:
        print("\nNo trading history available for analysis")

    client.disconnect()


def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("MT5History Usage Examples")
    print("="*60)

    examples = [
        ("Basic History Retrieval", example1_basic_history),
        ("Date Range History", example2_date_range_history),
        ("Filtered History", example3_filtered_history),
        ("Quick Access Methods", example4_quick_access),
        ("Performance Metrics", example5_performance_metrics),
        ("Trade Analysis", example6_trade_analysis),
        ("Winning vs Losing Trades", example7_winning_losing_trades),
        ("Report Generation", example8_report_generation),
        ("Export Data", example9_export_data),
        ("Comprehensive Analysis", example10_comprehensive_analysis),
    ]

    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")

    # Run a few examples by default
    try:
        example1_basic_history()
        example2_date_range_history()
        example4_quick_access()
        example5_performance_metrics()
        example6_trade_analysis()
        example7_winning_losing_trades()
        example10_comprehensive_analysis()

        print("\n" + "="*60)
        print("All examples completed successfully!")
        print("="*60)

    except Exception as e:
        logger.error(f"Error running examples: {e}")
        print(f"\nError: {e}")
        print("Make sure MT5 is running, you have valid credentials configured,")
        print("and you have some trading history available.")


if __name__ == "__main__":
    main()
