import datetime

today_date = datetime.datetime.today().strftime('%Y-%m-%d')

CONFIG = {
    'TICKERS': ['PHAT','VRTX'],
    'START_DATE': '2024-01-01',  # You can keep this static or update it to today's date
    'END_DATE': today_date,  # This will set the END_DATE to today's date
    'BASE_DIR': 'ticker_data',
    'USER_AGENT': 'Your Name your@email.com',
    'BENCHMARK_TICKERS': ['XBI','SPY'],
    'DATABASE_PATH':'ticker_data.db'
}
