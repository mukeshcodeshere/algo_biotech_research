import yfinance as yf
import sqlite3
import os
from config import CONFIG

def clear_database(conn):
    """
    Clears all tables from the SQLite database by dropping them.
    """
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        # Drop each table in the database
        for table in tables:
            table_name = table[0]
            print(f"Dropping table: {table_name}")
            cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
        
        conn.commit()
        print("All tables cleared.")
    except Exception as e:
        print(f"Error clearing the database: {e}")

def create_table(conn, ticker):
    """
    Creates a table for the ticker if it doesn't exist.
    """
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
    """
    data.index = data.index.strftime('%Y-%m-%d')  # Convert Date index to string format

    insert_query = f'''
    INSERT OR REPLACE INTO {ticker} (Date, Open, High, Low, Close, Adj_Close, Volume)
    VALUES (?, ?, ?, ?, ?, ?, ?);
    '''
    
    rows = [tuple(x) for x in data.reset_index().values]
    conn.executemany(insert_query, rows)
    conn.commit()

def download_data(tickers, start_date, end_date, db_path):
    """
    Downloads stock data for the given tickers and stores it in an SQLite database.
    """
    conn = sqlite3.connect(db_path)

    # Clear tables only at the beginning, not after data insertion
    #clear_database(conn)

    for ticker in tickers:
        try:
            print(f"Downloading data for {ticker}...")
            data = yf.download(ticker, start=start_date, end=end_date)
            
            if data.empty:
                print(f"No data found for {ticker}. Skipping...")
                continue

            create_table(conn, ticker)
            insert_data(conn, ticker, data)
            print(f"Data for {ticker} inserted into database.")

        except Exception as e:
            print(f"Error downloading data for {ticker}: {e}")
    
    conn.close()

def main():
    tickers = CONFIG['TICKERS']
    start_date = CONFIG['START_DATE']
    end_date = CONFIG['END_DATE']
    db_path = CONFIG['DATABASE_PATH']

    download_data(tickers, start_date, end_date, db_path)

    benchmark_tickers = CONFIG['BENCHMARK_TICKERS']
    download_data(benchmark_tickers, start_date, end_date, db_path)

if __name__ == "__main__":
    main()
