import time
import stockData
import live_strategy_handler
import multiprocessing as mp
import mongo

from strategies_live import ema_strategy_live
from strategies_live import random_live
# Ha a stockData-ban tovább tart valamennyi mp-nél a response time akkor probálja ujra

all_symbols = ['NVDA', 'TSLA', 'TQQQ', 'AMD', 'INTC', 'AMC', 'SHOP', 'ENVX', 'GOOG']
test_symbols = ['NVDA', 'TSLA', 'TQQQ']

lsh = live_strategy_handler.strategy_handler()
start_data = stockData.get_data_multiple_symbols(all_symbols, timeframe='15m', period='20d')
start_data_30m = stockData.get_data_multiple_symbols(all_symbols, timeframe='30m', period='40d')
start_data_60m = stockData.get_data_multiple_symbols(all_symbols, timeframe='60m', period='60d')
lsh.add_strategy(all_symbols, '200ema', start_data, start_data_30m, start_data_60m)
lsh.add_strategy(all_symbols, 'random', start_data, start_data_30m, start_data_60m)

print('Running strategies')

while True:
    # print('Running strategies_backtest')
    start = time.time()
    res = stockData.get_data_multiple_symbols(all_symbols, timeframe='15m', period='20d')
    res_30m = stockData.get_data_multiple_symbols(all_symbols, timeframe='30m', period='40d')
    res_60m = stockData.get_data_multiple_symbols(all_symbols, timeframe='60m', period='60d')
    response_end = time.time()
    lsh.run_strategies(res, res_30m, res_60m)
    print(f'Strategies ran in {time.time() - start}, response time: {response_end - start}')


