import yfinance as yf
import sqlite3
import os
from config import CONFIG
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.DEBUG)

def get_last_date_in_db(conn, ticker):
    """
    Fetch the most recent date available for a specific ticker in the database.
    """
    query = f"SELECT MAX(Date) FROM {ticker}"
    cursor = conn.cursor()
    cursor.execute(query)
    last_date = cursor.fetchone()[0]
    return last_date

def create_table(conn, ticker):
    """
    Creates a table for the ticker if it doesn't exist.
    """
    try:
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
        logging.debug(f"Table for {ticker} created or already exists.")
    except Exception as e:
        logging.error(f"Error creating table for {ticker}: {e}")

def insert_data(conn, ticker, data):
    """
    Inserts stock data into the SQLite database for a specific ticker.
    """
    data.index = data.index.strftime('%Y-%m-%d %H:%M:%S')  # Ensure timestamp format (date + time)

    insert_query = f'''
    INSERT OR REPLACE INTO {ticker} (Date, Open, High, Low, Close, Adj_Close, Volume)
    VALUES (?, ?, ?, ?, ?, ?, ?);
    '''
    rows = [tuple(x) for x in data.reset_index().values]
    conn.executemany(insert_query, rows)
    conn.commit()

def download_data(tickers, db_path):
    logging.debug(f"Tracking tickers: {tickers}")
    """
    Downloads stock data for the given tickers and stores it in an SQLite database.
    Downloads only the new data after the most recent date in the database.
    """
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)

    for ticker in tickers:
        try:
            print(f"Preparing table for {ticker}...")

            # Ensure the table exists in the database
            create_table(conn, ticker)

            # Get the last date available in the database
            last_date = get_last_date_in_db(conn, ticker)

            # If there's no data yet, set the start date to a very early date
            if last_date is None:
                last_date = '2024-11-12'

            # Get today's date and calculate the end date (7 days from today, Yahoo Finance limit)
            today = datetime.today()
            seven_days_later = today + timedelta(days=7)
            end_date = seven_days_later.strftime('%Y-%m-%d')

            logging.debug(f"Downloading data from {last_date} to {end_date} for {ticker}")

            # Define a limit for the number of days (max 8 days per request)
            chunk_size = 8  # Max number of days per request for 1-minute data
            start_date = datetime.strptime(last_date, '%Y-%m-%d')

            while start_date < today:
                chunk_end_date = start_date + timedelta(days=chunk_size)
                if chunk_end_date > today:
                    chunk_end_date = today  # Prevent going past today

                # Download data for the current chunk
                logging.debug(f"Downloading data for {ticker} from {start_date.date()} to {chunk_end_date.date()}")
                data = yf.download(ticker, start=start_date.date(), end=chunk_end_date.date(), interval="1m", progress=False)

                if data.empty:
                    print(f"No new data found for {ticker}. Skipping...")
                    break

                # Insert new data into the database
                logging.debug(f"Data for {ticker}: {data.tail()}")
                insert_data(conn, ticker, data)
                print(f"New data for {ticker} inserted into database.")

                # Update the start date for the next chunk
                start_date = chunk_end_date

        except Exception as e:
            print(f"Error downloading data for {ticker}: {e}")
    
    # Close the database connection
    conn.close()

def main():
    # Get the tickers from the configuration
    tickers = CONFIG['TICKERS']
    db_path = CONFIG['DATABASE_PATH']

    # Download the new data for all tickers
    download_data(tickers, db_path)

    # Download data for benchmark tickers
    benchmark_tickers = CONFIG['BENCHMARK_TICKERS']
    download_data(benchmark_tickers, db_path)

if __name__ == "__main__":
    main()
