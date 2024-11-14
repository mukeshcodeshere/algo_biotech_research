import yfinance as yf
import sqlite3
import os
from config import CONFIG

def create_table(conn, ticker):
    """
    Creates a table in the SQLite database for a specific ticker if it doesn't exist.
    
    :param conn: SQLite database connection
    :param ticker: Ticker symbol (e.g., 'AAPL')
    :return: None
    """
    # Define the SQL query to create a table with the appropriate schema
    create_table_query = f'''
    CREATE TABLE IF NOT EXISTS {ticker} (
        Date TEXT PRIMARY KEY,
        Open REAL,
        High REAL,
        Low REAL,
        Close REAL,
        Adj_Close REAL,
        Volume INTEGER
    );
    '''
    conn.execute(create_table_query)
    conn.commit()

def insert_data(conn, ticker, data):
    """
    Inserts stock data into the SQLite database for a specific ticker.
    
    :param conn: SQLite database connection
    :param ticker: Ticker symbol (e.g., 'AAPL')
    :param data: DataFrame containing stock data
    :return: None
    """
    # Convert the Date index to a string format (YYYY-MM-DD)
    data.index = data.index.strftime('%Y-%m-%d')
    
    # Prepare the SQL query for inserting data
    insert_query = f'''
    INSERT OR REPLACE INTO {ticker} (Date, Open, High, Low, Close, Adj_Close, Volume)
    VALUES (?, ?, ?, ?, ?, ?, ?);
    '''
    
    # Convert the data into a list of tuples (one per row)
    rows = [tuple(x) for x in data.reset_index().values]
    
    # Insert data into the database
    conn.executemany(insert_query, rows)
    conn.commit()

def download_data(tickers, start_date, end_date, db_path):
    """
    Downloads stock data for the given tickers and stores it in an SQLite database.
    
    :param tickers: List of stock ticker symbols (e.g., ['AAPL', 'GOOG'])
    :param start_date: Start date for the data download (e.g., '2024-01-01')
    :param end_date: End date for the data download (e.g., '2024-11-14')
    :param db_path: Path to the SQLite database
    :return: None
    """
    # Connect to SQLite database (it will create the DB if it doesn't exist)
    conn = sqlite3.connect(db_path)
    
    for ticker in tickers:
        try:
            print(f"Downloading data for {ticker}...")
            data = yf.download(ticker, start=start_date, end=end_date)
            
            # If data is empty, skip saving it
            if data.empty:
                print(f"No data found for {ticker}. Skipping...")
                continue

            # Create the table for the ticker if it doesn't exist
            create_table(conn, ticker)
            
            # Insert the data into the database
            insert_data(conn, ticker, data)
            print(f"Data for {ticker} inserted into database.")
        
        except Exception as e:
            print(f"Error downloading data for {ticker}: {e}")
    
    conn.close()

def main():
    # Get configuration values
    tickers = CONFIG['TICKERS']
    start_date = CONFIG['START_DATE']
    end_date = CONFIG['END_DATE']
    db_path = CONFIG['DATABASE_PATH']  # Local SQLite database path
    
    # Download and store data for the tickers
    download_data(tickers, start_date, end_date, db_path)
    
    # Optionally, download benchmark data (XBI, SPY)
    benchmark_tickers = CONFIG['BENCHMARK_TICKERS']
    download_data(benchmark_tickers, start_date, end_date, db_path)

if __name__ == "__main__":
    main()
