import sqlite3
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config2 import CONFIG
import io
import sys

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

def track_stocks(tickers, benchmark_ticker, db_path, output_buffer):
    """
    Tracks a list of tickers and flags those that have moved more than 10% compared to the benchmark.
    
    :param tickers: List of tickers to track (e.g., ['AAPL', 'GOOG'])
    :param benchmark_ticker: Benchmark ticker (e.g., 'SPY')
    :param db_path: Path to the SQLite database
    :param output_buffer: A StringIO buffer to capture the print output
    :return: None
    """
    # Fetch benchmark data
    benchmark_data = fetch_data_from_db(benchmark_ticker, db_path)
    
    # Calculate benchmark's percentage change
    benchmark_change = calculate_percentage_change(benchmark_data)
    
    # Write output to buffer
    output_buffer.write(f"Benchmark ({benchmark_ticker}) Percentage Change: {benchmark_change:.2f}%\n")
    
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
                output_buffer.write(f"ALERT: {ticker} is UP by {stock_change:.2f}% while benchmark is UP by {benchmark_change:.2f}%\n")
            else:
                output_buffer.write(f"ALERT: {ticker} is DOWN by {stock_change:.2f}% while benchmark is UP by {benchmark_change:.2f}%\n")

def send_email(subject, body, to_email, from_email, smtp_server, smtp_port, smtp_user, smtp_password):
    """
    Sends an email with the given subject and body.
    
    :param subject: The subject of the email
    :param body: The body of the email
    :param to_email: Recipient email address
    :param from_email: Sender email address
    :param smtp_server: SMTP server address (e.g., 'smtp.gmail.com')
    :param smtp_port: SMTP server port (e.g., 587 for Gmail)
    :param smtp_user: SMTP username
    :param smtp_password: SMTP password
    :return: None
    """
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    
    # Attach the email body
    msg.attach(MIMEText(body, 'plain'))
    
    # Set up the server and send the email
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Secure the connection
        server.login(smtp_user, smtp_password)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        print(f"Email sent successfully to {to_email}")
    except Exception as e:
        print(f"Error sending email: {e}")

def main():
    # Fetch configuration details
    tickers = CONFIG['TICKERS']
    benchmark_tickers = CONFIG['BENCHMARK_TICKERS']
    db_path = CONFIG['DATABASE_PATH']  # SQLite database path
    
    # Capture print output
    output_buffer = io.StringIO()
    sys.stdout = output_buffer  # Redirect stdout to the buffer
    
    # Track stocks for each benchmark ticker
    for benchmark_ticker in benchmark_tickers:
        print(f"\nTracking with benchmark: {benchmark_ticker}")
        track_stocks(tickers, benchmark_ticker, db_path, output_buffer)

    # Get the captured output
    email_body = output_buffer.getvalue()
    
    # Send email with the captured output
    subject = "Stock Tracking Alerts"
    to_email = CONFIG['TO_EMAIL']
    from_email = CONFIG['FROM_EMAIL']
    smtp_server = CONFIG['SMTP_SERVER']
    smtp_port = CONFIG['SMTP_PORT']
    smtp_user = CONFIG['SMTP_USER']
    smtp_password = CONFIG['SMTP_PASSWORD']
    
    send_email(subject, email_body, to_email, from_email, smtp_server, smtp_port, smtp_user, smtp_password)

if __name__ == "__main__":
    main()
