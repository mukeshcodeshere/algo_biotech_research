## Instructions to run scripts

Inputs --> config.py

 flag when a certain list of stocks are up/down 10% vs mean vs RSI vs XBI vs S&P / create 20 factors / which factors have been the most predictive ; algorithm research, deployment after SEC data downloader

 1) Download Script -> python data_download.py
 2) Track indiviudal ticker against benchmark -> python ticker_tracker.py
 3) Benchmark tracking -> python benchmark_tracker.py
 4) Email Script -> testmail.py --> Blocked by firewall ; nothing from Bjoern yet
 5) Live minute by minute update and tracking -> schedule_scripts.py 