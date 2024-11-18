import datetime

today_date = datetime.datetime.today().strftime('%Y-%m-%d')
start_date = (datetime.datetime.today() - datetime.timedelta(days=30)).strftime('%Y-%m-%d') # PRIOR 30 DAYS

CONFIG = {
    'TICKERS': ['PHAT','VRTX','REGN','BNTX','INCY','MRNA','ALNY','UTHR','ARGX','BGNE'],
    'START_DATE': start_date,  # You can keep this static or update it to today's date
    'END_DATE': today_date,  # This will set the END_DATE to today's date
    'BASE_DIR': 'ticker_data',
    'USER_AGENT': 'Your Name your@email.com',
    'BENCHMARK_TICKERS': ['XBI','SPY'],
    'DATABASE_PATH':'ticker_data.db'
}
