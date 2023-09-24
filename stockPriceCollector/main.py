import time

import stockData
import configparser
import mongo
from datetime import datetime

config = configparser.ConfigParser()
config.read('config.ini')

symbols = config['PRICE-DATA']['symbols'].split(',')
timeframes = config['PRICE-DATA']['timeframes'].split(',')
for a in symbols:
    a.upper()
for b in timeframes:
    b.lower()

print(f'Running on symbols: {symbols}')
session_requests = 0
while True:
    start = time.time()
    for timeframe in timeframes:
        data = stockData.get_data(symbols, timeframe, '60d')
        for symbol in symbols:
            mongo.add_data_with_history(symbol,
                                        list(data['Open'][symbol]),
                                        list(data['High'][symbol]),
                                        list(data['Low'][symbol]),
                                        list(data['Close'][symbol]),
                                        list(data['Volume'][symbol]),
                                        list(data['DateTime']), timeframe, '60d')
    session_requests += 1
    print(f'[{datetime.now().strftime("%H:%M:%S")}] Run time: {time.time() - start} | requests this session: {session_requests}')