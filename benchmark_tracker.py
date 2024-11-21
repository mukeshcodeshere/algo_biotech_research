import sqlite3
import pandas as pd
import time
from datetime import datetime
from config import CONFIG
import logging

logging.basicConfig(level=logging.DEBUG)

def fetch_data_from_db(ticker, db_path, limit=50):
    """
    Fetches historical stock data (date and close price) for a given ticker from the SQLite database.
    :param ticker: Stock ticker symbol (e.g., 'AAPL')
    :param db_path: Path to the SQLite database
    :param limit: Number of records to fetch (default is 50, can be adjusted based on RSI needs)
    :return: DataFrame containing the stock data
    """
    conn = sqlite3.connect(db_path)
    
    # Fetch the most recent 'limit' number of rows for the ticker (get Date and Close)
    query = f"SELECT Date, Close FROM {ticker} ORDER BY Date DESC LIMIT {limit}"
    data = pd.read_sql(query, conn)
    
    conn.close()
    
    # Convert 'Date' to datetime and set it as the index
    data['Date'] = pd.to_datetime(data['Date'])
    data.set_index('Date', inplace=True)
    
    return data

def calculate_percentage_change(start_price, end_price):
    """
    Calculates the percentage change in closing price for a stock.
    :param start_price: The starting price
    :param end_price: The ending price
    :return: Percentage change in price
    """
    return ((end_price - start_price) / start_price) * 100

def calculate_rsi(data, period=14): # 14 days or 14 periods of time????
    """
    Calculates the Relative Strength Index (RSI) for a given price series.
    :param data: Pandas DataFrame with 'Close' prices
    :param period: The period over which to calculate RSI (default is 14 days)
    :return: RSI value and the date of the last data point
    """
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    avg_gain = gain.rolling(window=period, min_periods=1).mean()
    avg_loss = loss.rolling(window=period, min_periods=1).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi.iloc[-1], data.index[-1]  # Return RSI value and the date of the last data point

def check_for_alerts(benchmark_ticker, db_path, last_benchmark_price, alert_threshold=5, rsi_thresholds=(30, 70)):
    """
    Checks if the benchmark has moved by more than the specified threshold (e.g., 5%) or if RSI crosses overbought/oversold thresholds.
    :param benchmark_ticker: Benchmark ticker (e.g., 'SPY')
    :param db_path: Path to the SQLite database
    :param last_benchmark_price: The last recorded benchmark price
    :param alert_threshold: The percentage change threshold for triggering an alert
    :param rsi_thresholds: Tuple of RSI thresholds (oversold, overbought)
    :return: None
    """
    # Fetch benchmark data
    benchmark_data = fetch_data_from_db(benchmark_ticker, db_path)
    benchmark_price = benchmark_data['Close'].iloc[0]
    benchmark_date = benchmark_data.index[0]  # The date of the latest price
    
    # Calculate benchmark's percentage change
    benchmark_change = calculate_percentage_change(last_benchmark_price, benchmark_price)
    
    # Get current timestamp
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Print current price and calculate percentage change
    print(f"[{current_time}] Latest price for {benchmark_ticker}: {benchmark_price:.2f} on {benchmark_date.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if price change exceeds the alert threshold
    if abs(benchmark_change) >= alert_threshold:
        print(f"[{current_time}] ALERT: Benchmark {benchmark_ticker} has moved by {benchmark_change:.2f}%")
        if benchmark_change > 0:
            print(f"  - {benchmark_ticker} went UP by {benchmark_change:.2f}%")
        else:
            print(f"  - {benchmark_ticker} went DOWN by {benchmark_change:.2f}%")
    
    # Calculate the RSI for the benchmark ticker
    rsi, rsi_date = calculate_rsi(benchmark_data)
    print(f"[{current_time}] RSI for {benchmark_ticker} as of {rsi_date.strftime('%Y-%m-%d %H:%M:%S')}: {rsi:.2f}")
    
    # Check if RSI is overbought or oversold
    if rsi > rsi_thresholds[1]:
        print(f"  - ALERT: {benchmark_ticker} is OVERBOUGHT (RSI > 70)!")
    elif rsi < rsi_thresholds[0]:
        print(f"  - ALERT: {benchmark_ticker} is OVERSOLD (RSI < 30)!")
    
    return benchmark_price

def track_live(benchmark_tickers, db_path, alert_threshold=5, refresh_interval=60, rsi_thresholds=(30, 70)):
    """
    Continuously track benchmark prices, triggering an alert if a significant change occurs or if RSI crosses thresholds.
    :param benchmark_tickers: List of benchmark tickers to track
    :param db_path: Path to the SQLite database
    :param alert_threshold: Percentage change threshold for triggering an alert
    :param refresh_interval: How often to refresh and check prices (in seconds)
    :param rsi_thresholds: Tuple of RSI thresholds (oversold, overbought)
    :return: None
    """
    last_benchmark_prices = {ticker: None for ticker in benchmark_tickers}

    while True:
        for benchmark_ticker in benchmark_tickers:
            # If it's the first time, fetch the benchmark price
            if last_benchmark_prices[benchmark_ticker] is None:
                benchmark_data = fetch_data_from_db(benchmark_ticker, db_path)
                last_benchmark_prices[benchmark_ticker] = benchmark_data['Close'].iloc[0]
            
            # Check for alerts based on the latest data
            last_benchmark_prices[benchmark_ticker] = check_for_alerts(
                benchmark_ticker, db_path, last_benchmark_prices[benchmark_ticker], alert_threshold, rsi_thresholds
            )
        
        # Wait for the specified refresh interval before checking again
        time.sleep(refresh_interval)

def main():
    # Fetch configuration details
    benchmark_tickers = CONFIG['BENCHMARK_TICKERS']
    db_path = CONFIG['DATABASE_PATH']  # SQLite database path
    
    # Track live for each benchmark ticker
    print(f"\nStarting live tracking with benchmark tickers: {', '.join(benchmark_tickers)}")
    track_live(benchmark_tickers, db_path)

if __name__ == "__main__":
    main()
