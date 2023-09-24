import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import time
import pandas as pd
import pandas_ta as ta
import mongoHandler as mongo
import configparser
import OrderHandlerLive

class strategy:
    def __init__(self, symbol: str, rtr_ratio=2.0, atr_multiplier=2.0):
        self.symbol = symbol.upper()
        self.strategy_name = 'macd_bollinger'
        self.mongo_chart_id = 3
        self.rtr_ratio = rtr_ratio
        self.atr_multiplier = atr_multiplier
        self.data15m = mongo.get_price_data(self.symbol, '15m')
        self.order_handler = OrderHandlerLive.OrderHandlerLive(self.symbol, '15m', self.data15m, self.strategy_name,
                                                               create_chart_subplot=True)
        self.chart = self.order_handler.chart

    def update_data(self):
        data = mongo.get_price_data(self.symbol, '15m')
        if data is None: return
        try:
            self.data15m = data

            self.chart.update_chart(self.data15m)
            if self.order_handler.position is not None:
                mongo.update_pnl(self.order_handler.position, self.data15m.iloc[len(self.data15m) - 1])

            macd = ta.macd(self.data15m['Close'])
            self.data15m['macd_fast'], self.data15m['macd_hist'], self.data15m['macd_slow'] = macd['MACD_12_26_9'], \
                                                                                              macd['MACDh_12_26_9'], \
                                                                                              macd['MACDs_12_26_9']
            bands = ta.bbands(self.data15m['macd_hist'], length=10)
            self.data15m['bb_lower'], self.data15m['bb_upper'] = bands['BBL_10_2.0'], bands['BBU_10_2.0']
            self.data15m['atr'] = ta.atr(self.data15m['High'], self.data15m['Low'], self.data15m['Close'])

            self.chart.add_subplot_data(self.data15m['bb_lower'], graph_type='line')
            self.chart.add_subplot_data(self.data15m['bb_upper'], graph_type='line')
            self.chart.add_subplot_data(self.data15m['macd_hist'], graph_type='bar', color='green')

        except:
            return

    def run_strategy(self):
        self.update_data()
        current_candle = self.previous_candle()
        previous_candle = self.previous_candle(1)
        self.order_handler.check_position(current_candle)
        if self.order_handler.position is not None:
            return None, self.chart.chart, self.mongo_chart_id

        if previous_candle['macd_hist'] > previous_candle['bb_lower'] and current_candle['macd_hist'] < current_candle['bb_lower']:
            stop_loss = current_candle['Close'] - (current_candle['atr'] * self.atr_multiplier)
            target_price = current_candle['Close'] + (current_candle['Close'] - stop_loss) * self.rtr_ratio

            self.order_handler.open_position(order_type='long',
                                             buy_candle=current_candle,
                                             target_price=target_price,
                                             stop_loss=stop_loss,
                                             info=True)

        elif previous_candle['macd_hist'] < previous_candle['bb_upper'] and current_candle['macd_hist'] > current_candle['bb_upper']:
            stop_loss = current_candle['Close'] + (current_candle['atr'] * self.atr_multiplier)
            target_price = current_candle['Close'] - (stop_loss - current_candle['Close']) * self.rtr_ratio

            self.order_handler.open_position(order_type='short',
                                             buy_candle=current_candle,
                                             target_price=target_price,
                                             stop_loss=stop_loss,
                                             info=True)

        return None, self.chart.chart, self.mongo_chart_id

    def previous_candle(self, n=0):
        return self.data15m.iloc[len(self.data15m) - n - 1]


# --------------------------------------------------------------------------


strategy_holder = []
config = configparser.ConfigParser()
config.read('macd_bollinger_config.ini')

symbols = config['SETTINGS']['symbols'].split(',')
timeframe = config['SETTINGS']['timeframe']
show_runtime = bool(config['SETTINGS']['show_runtime'])
sleep_time = float(config['SETTINGS']['sleep_time'])

if show_runtime == 'True' or show_runtime == 'true':
    show_runtime = True
else:
    show_runtime = False

for symbol in symbols:
    strategy_holder.append(strategy(symbol.upper(),
                                    rtr_ratio=float(config['SETTINGS']['rtr_ratio']),
                                    atr_multiplier=float(config['SETTINGS']['atr_multiplier'])))

print(f'\nRunning strategy (macd_bollinger) on symbols: {symbols}\n')


while True:
    time.sleep(sleep_time)
    start = time.time()
    for strategy in strategy_holder:
        result = strategy.run_strategy()
        mongo.add_chart_to_db(strategy.symbol, result[1], strategy.strategy_name, result[2])

    if show_runtime:
        print(f'Strategy ran on all symbols in {time.time() - start}s')