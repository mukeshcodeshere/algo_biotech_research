import sqlite3
import pandas as pd
from config import CONFIG

def fetch_data_from_db(ticker, db_path):
    """
    Fetches stock data (date and close price) for a given ticker from the SQLite database.
    
    :param ticker: Stock ticker symbol (e.g., 'AAPL')
    :param db_path: Path to the SQLite database
    :return: DataFrame containing the stock data
    """
    conn = sqlite3.connect(db_path)
    
    # Fetch data for the ticker from the database (get Date and Close)
    query = f"SELECT Date, Close FROM {ticker} ORDER BY Date"
    data = pd.read_sql(query, conn)
    
    conn.close()
    
    # Convert 'Date' to datetime and set it as the index
    data['Date'] = pd.to_datetime(data['Date'])
    data.set_index('Date', inplace=True)
    
    return data

def calculate_percentage_change(data):
    """
    Calculates the percentage change in closing price for a stock.
    
    :param data: DataFrame containing stock data with 'Close' price
    :return: Percentage change in price from the first to the last date
    """
    # Calculate percentage change from the first date to the last date
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
        
        # Compare stock's percentage change with benchmark
        difference = abs(stock_change - benchmark_change)
        
        # If the difference is greater than 10%, flag it
        if difference >= 10:
            if stock_change > benchmark_change:
                print(f"ALERT: {ticker} is UP by {stock_change:.2f}% while benchmark is UP by {benchmark_change:.2f}%")
            else:
                print(f"ALERT: {ticker} is DOWN by {stock_change:.2f}% while benchmark is UP by {benchmark_change:.2f}%")

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
