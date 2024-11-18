import sqlite3
import pandas as pd
from config import CONFIG
from datetime import datetime, timedelta

def fetch_data_from_db(ticker, db_path):
    """
    Fetches stock data (timestamp, close price) for a given ticker from the SQLite database.
    
    :param ticker: Stock ticker symbol (e.g., 'AAPL')
    :param db_path: Path to the SQLite database
    :return: DataFrame containing the stock data
    """
    conn = sqlite3.connect(db_path)

    # Calculate the date 3 days ago
    three_days_ago = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')    
    # Fetch minute-level data for the ticker from the database (get Date, Time, Close)
    query = f"SELECT Date, Close FROM {ticker} WHERE Date >= {three_days_ago} ORDER BY Date"
    data = pd.read_sql(query, conn)
    
    conn.close()
    
    # Combine Date and Time into a single datetime column
    data['Datetime'] = pd.to_datetime(data['Date'])
    data.set_index('Datetime', inplace=True)
    
    # Drop the individual 'Date'
    data.drop(['Date'], axis=1, inplace=True)
    
    return data

def calculate_percentage_change(data):
    """
    Calculates the percentage change in closing price for a stock from the first to the last timestamp.
    
    :param data: DataFrame containing stock data with 'Close' price
    :return: Percentage change in price from the first to the last timestamp
    """
    # Calculate percentage change from the first timestamp to the last timestamp
    start_price = data['Close'].iloc[0]
    end_price = data['Close'].iloc[-1]
    
    return ((end_price - start_price) / start_price) * 100

def track_stocks(tickers, benchmark_ticker, db_path):
    """
    Tracks a list of tickers and flags those that have moved more than 10% compared to the benchmark.
    
    :param tickers: List of tickers to track (e.g., ['AAPL', 'GOOG'])
    :param benchmark_ticker: Benchmark ticker (e.g., 'SPY')
    :param db_path: Path to the SQLite database
    :return: None
    """
    # Fetch benchmark data
    benchmark_data = fetch_data_from_db(benchmark_ticker, db_path)
    
    # Calculate benchmark's percentage change
    benchmark_change = calculate_percentage_change(benchmark_data)
    
    print(f"Benchmark ({benchmark_ticker}) Percentage Change: {benchmark_change:.2f}%")
    
    # Iterate through tickers and calculate their percentage change
    for ticker in tickers:
        # Fetch stock data
        stock_data = fetch_data_from_db(ticker, db_path)
        
        # Calculate stock's percentage change
        stock_change = calculate_percentage_change(stock_data)
        
        # Get the time of the first and last data points
        first_time = stock_data.index[0]
        last_time = stock_data.index[-1]
        
        # Compare stock's percentage change with benchmark
        difference = abs(stock_change - benchmark_change)
        
        # If the difference is greater than 10%, flag it
        if difference >= 10:
            if stock_change > benchmark_change:
                print(f"ALERT: {ticker} is UP by {stock_change:.2f}% from {first_time} to {last_time}, "
                      f"while benchmark is UP by {benchmark_change:.2f}%")
            else:
                print(f"ALERT: {ticker} is DOWN by {stock_change:.2f}% from {first_time} to {last_time}, "
                      f"while benchmark is UP by {benchmark_change:.2f}%")

def main():
    # Fetch configuration details
    tickers = CONFIG['TICKERS']
    benchmark_tickers = CONFIG['BENCHMARK_TICKERS']
    db_path = CONFIG['DATABASE_PATH']  # SQLite database path
    
    # Track stocks for each benchmark ticker
    for benchmark_ticker in benchmark_tickers:
        print(f"\nTracking with benchmark: {benchmark_ticker}")
        track_stocks(tickers, benchmark_ticker, db_path)

if __name__ == "__main__":
    main()
