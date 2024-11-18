import schedule
import time
from benchmark_tracker import track_live  # Assuming you imported track_live from your main tracking script
from config import CONFIG
import subprocess

def run_data_download():
    """
    Runs the data download process before starting live tracking.
    """
    print("Running data download...")
    
    # Run the data download script (assuming it's a standalone script)
    subprocess.run(["python", "data_download.py"], check=True)

def run_ticker_tracker():
    """
    Runs the ticker tracking process, checking if any stocks moved more than 10% compared to the benchmark.
    """
    print("Running ticker tracking...")
    
    # Run the ticker tracker script
    subprocess.run(["python", "ticker_tracker.py"], check=True)

def run_tracking():
    """
    Starts the live tracking process.
    """
    benchmark_tickers = CONFIG['BENCHMARK_TICKERS']
    db_path = CONFIG['DATABASE_PATH']
    print(f"\nStarting live tracking with benchmark tickers: {', '.join(benchmark_tickers)}")
    track_live(benchmark_tickers, db_path)

# Schedule the tasks
schedule.every(60).seconds.do(run_data_download)  # Download data every 60 seconds
schedule.every(60).seconds.do(run_ticker_tracker)  # Track stock movements every 60 seconds
schedule.every(60).seconds.do(run_tracking)  # Track live every 60 seconds (adjust as needed)

while True:
    schedule.run_pending()  # Run scheduled tasks
    time.sleep(1)  # Sleep for a short time to avoid CPU overuse
