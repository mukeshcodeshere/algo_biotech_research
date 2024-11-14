import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
from config import CONFIG

def fetch_data_from_db(ticker, db_path):
    """
    Fetches the stock data for a given ticker from the SQLite database.
    
    :param ticker: Stock ticker symbol (e.g., 'AAPL')
    :param db_path: Path to the SQLite database
    :return: DataFrame containing the stock data
    """
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    
    # Query the data from the database
    query = f"SELECT Date, Close FROM {ticker} ORDER BY Date"
    data = pd.read_sql(query, conn)
    
    # Close the connection
    conn.close()
    
    # Convert Date column to datetime format
    data['Date'] = pd.to_datetime(data['Date'])
    
    return data

def plot_ticker_data(ticker, db_path):
    """
    Plots the closing price for a given ticker.
    
    :param ticker: Stock ticker symbol (e.g., 'AAPL')
    :param db_path: Path to the SQLite database
    :return: None
    """
    # Fetch the stock data from the database
    data = fetch_data_from_db(ticker, db_path)
    
    if data.empty:
        print(f"No data found for {ticker}. Skipping plot.")
        return
    
    # Plot the closing price
    plt.figure(figsize=(10, 6))
    plt.plot(data['Date'], data['Close'], label=f'{ticker} Closing Price', color='blue')
    plt.title(f'{ticker} Stock Price Over Time')
    plt.xlabel('Date')
    plt.ylabel('Closing Price (USD)')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    
    # Show the plot
    plt.show()

def get_tickers_from_db(db_path):
    """
    Fetches the list of tickers from the SQLite database.
    
    :param db_path: Path to the SQLite database
    :return: List of tickers present in the database
    """
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    
    # Query the list of tables (tickers)
    query = "SELECT name FROM sqlite_master WHERE type='table';"
    tables = pd.read_sql(query, conn)
    
    # Close the connection
    conn.close()
    
    # Extract the table names (these correspond to the tickers)
    tickers = tables['name'].tolist()
    
    return tickers

def main():
    # Get the database path from the configuration file
    db_path = CONFIG['DATABASE_PATH']  # Ensure this is set correctly in configy.py
    
    # Get the list of tickers from the database
    tickers = get_tickers_from_db(db_path)
    
    if not tickers:
        print("No tickers found in the database. Exiting.")
        return
    
    # Plot data for each ticker
    for ticker in tickers:
        plot_ticker_data(ticker, db_path)

if __name__ == "__main__":
    main()
