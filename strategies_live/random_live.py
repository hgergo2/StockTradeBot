import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

import random
import time

import mongoHandler as mongo
import OrderHandlerLive
import pandas as pd
import configparser
import pandas_ta as ta


class strategy:
    def __init__(self, symbol: str):
        self.symbol = symbol.upper()
        self.strategy_name = 'random_strategy'
        self.mongo_chart_id = 1
        self.data15m = mongo.get_price_data(symbol, '15m')
        self.data15m['atr'] = ta.atr(self.data15m['High'], self.data15m['Low'], self.data15m['Close'])
        self.order_handler = OrderHandlerLive.OrderHandlerLive(self.symbol, '15m', self.data15m, self.strategy_name)
        self.chart = self.order_handler.chart

    def update_data(self):
        data = mongo.get_price_data(self.symbol, '15m')
        if data is None: return
        try:
            self.data15m = data
            self.chart.update_chart(self.data15m)
            if self.order_handler.position is not None:
                mongo.update_pnl(self.order_handler.position, self.data15m.iloc[len(self.data15m) - 1])

            self.data15m['atr'] = ta.atr(self.data15m['High'], self.data15m['Low'], self.data15m['Close'])
        except:
            return

    def run_strategy(self, max_stop_loss=0.03, rtr_ratio=2.0, atr_multiplier=2.0):
        self.update_data()
        current_candle = self.previous_candle()
        self.order_handler.check_position(current_candle)
        if self.order_handler.position is not None:
            return None, self.chart.chart, self.mongo_chart_id

        rand = random.randint(1, 2)

        if rand == 1:
            stop_loss = current_candle['Close'] - (current_candle['atr'] * atr_multiplier)
            target_price = current_candle['Close'] + ((current_candle['Close'] - stop_loss) * rtr_ratio)

            if abs((stop_loss / current_candle['Close']) - 1) > max_stop_loss:
                print(f'stop loss was {abs(stop_loss / current_candle["Close"]) - 1}')
                stop_loss = current_candle['Close'] * (1 - max_stop_loss)

            self.order_handler.open_position(order_type='long',
                                             buy_candle=current_candle,
                                             info=True,
                                             target_price=target_price,
                                             stop_loss=stop_loss)
        else:
            stop_loss = current_candle['Close'] + (current_candle['atr'] * atr_multiplier)
            target_price = current_candle['Close'] - ((stop_loss - current_candle['Close']) * rtr_ratio)

            if abs((current_candle['Close'] / stop_loss) - 1) > max_stop_loss:
                print(f'stop loss was {abs(stop_loss / current_candle["Close"]) - 1}')
                stop_loss = current_candle['Close'] * (1 - max_stop_loss)

            self.order_handler.open_position(order_type='short',
                                             buy_candle=current_candle,
                                             info=True,
                                             target_price=target_price,
                                             stop_loss=stop_loss)

        return None, self.chart.chart, self.mongo_chart_id

    def previous_candle(self, n=0):
        return self.data15m.iloc[len(self.data15m) - n - 1]


# --------------------------------------------------------------------------


strategy_holder = []
config = configparser.ConfigParser()
config.read('random_strategy_config.ini')

symbols = config['SETTINGS']['symbols'].split(',')
timeframe = config['SETTINGS']['timeframe']
show_runtime = config['SETTINGS']['show_runtime']
sleep_time = float(config['SETTINGS']['sleep_time'])

# Strategy settings

max_stop_loss = float(config['SETTINGS']['max_stop_loss'])
rtr_ratio = float(config['SETTINGS']['rtr_ratio'])
atr_multiplier = float(config['SETTINGS']['atr_multiplier'])

if show_runtime == 'True' or show_runtime == 'true':
    show_runtime = True
    print('Show runtime is true')
else:
    show_runtime = False
    print('Show runtime is False')

for symbol in symbols:
    strategy_holder.append(strategy(symbol.upper()))

print(f'\nRunning strategy (random) on symbols: {symbols}\n')
print(f'--Strategy settings--\n'
      f'max_stop_loss: {max_stop_loss}\n'
      f'rtr_ratio: {rtr_ratio}\n'
      f'atr_multiplier: {atr_multiplier}')

while True:
    time.sleep(sleep_time)
    start = time.time()
    for strategy in strategy_holder:
        result = strategy.run_strategy()
        mongo.add_chart_to_db(strategy.symbol, result[1], strategy.strategy_name, result[2])

    if show_runtime:
        print(f'Strategy ran on all symbols in {time.time() - start}s')
