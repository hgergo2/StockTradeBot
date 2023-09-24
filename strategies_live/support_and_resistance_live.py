import configparser
import time
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import pandas as pd
import pandas_ta as ta
import OrderHandlerLive
import mongoHandler as mongo

def calc_long_zones(data, atr_multiplier):
    peaks = []
    current_peak_short = None

    for n in range(1, len(data)):
        current_candle = data.iloc[n]
        previous_candle = data.iloc[n - 1]

        if current_peak_short is None and previous_candle['Close'] < previous_candle['Open']:
            current_peak_short = current_candle
        if current_peak_short is not None:
            if current_candle['Close'] < current_peak_short['Close'] and previous_candle['Close'] < previous_candle[
                'Open']:
                current_peak_short = current_candle
            elif current_peak_short['Close'] + (current_peak_short['atr'] * atr_multiplier) < current_candle[
                'Close'] < \
                    data.iloc[n - 5]['Close']:

                peaks.append(current_peak_short)
                current_peak_short = None

    return peaks


def calc_zones(data, atr_multiplier):

    peaks = []
    current_peak_long = None
    current_peak_short = None

    for n in range(1, len(data)):
        current_candle = data.iloc[n]
        previous_candle = data.iloc[n - 1]

        if current_peak_long is None and previous_candle['Close'] > previous_candle['Open']:
            current_peak_long = current_candle
        if current_peak_long is not None:
            if current_candle['Close'] > current_peak_long['Close'] and previous_candle['Close'] > previous_candle[
                'Open']:
                current_peak_long = current_candle
            elif current_peak_long['Close'] - (current_peak_long['atr'] * atr_multiplier) > current_candle[
                'Close'] > \
                    data.iloc[n - 5]['Close']:

                peaks.append(current_peak_long)
                current_peak_long = None

        if current_peak_short is None and previous_candle['Close'] < previous_candle['Open']:
            current_peak_short = current_candle
        if current_peak_short is not None:
            if current_candle['Close'] < current_peak_short['Close'] and previous_candle['Close'] < previous_candle[
                'Open']:
                current_peak_short = current_candle
            elif current_peak_short['Close'] + (current_peak_short['atr'] * atr_multiplier) < current_candle[
                'Close'] < \
                    data.iloc[n - 5]['Close']:

                peaks.append(current_peak_short)
                current_peak_short = None


    return peaks


class strategy:
    def __init__(self, symbol: str, max_stop_loss=0.03, atr_multiplier=4.0, rtr_ratio=3.0):
        self.symbol = symbol.upper()
        self.strategy_name = 'support_and_resistance'
        self.mongo_chart_id = 2

        self.max_stop_loss = max_stop_loss
        self.atr_multiplier = atr_multiplier
        self.rtr_ratio = rtr_ratio

        self.data15m = mongo.get_price_data(self.symbol, '15m')
        self.order_handler = OrderHandlerLive.OrderHandlerLive(self.symbol, '15m', self.data15m, self.strategy_name)
        self.chart = self.order_handler.chart

    def update_data(self):
        data = mongo.get_price_data(self.symbol, '15m')
        if data is None: return

        try:
            self.data15m = data
            self.chart.update_chart(self.data15m)
            if self.order_handler.position is not None:
                mongo.update_pnl(self.order_handler.position, self.data15m.iloc[len(self.data15m)-1])

            self.data15m['atr'] = ta.atr(self.data15m['High'], self.data15m['Low'], self.data15m['Close'])
            self.data15m['avg_volume'] = ta.ma('sma', self.data15m['Volume'])


        except:
            return

    def run_strategy(self):
        self.update_data()
        #__peaks_short = calc_short_zones(self.data15m[-200:], atr_multiplier)
        #__peaks_long = calc_short_zones(self.data15m[-200:], atr_multiplier)
        #print(self.data15m[-500:].to_string())
        peaks = calc_zones(self.data15m[-200:], self.atr_multiplier)

        current_candle = self.previous_candle()
        previous_candle = self.previous_candle(1)
        self.order_handler.check_position(current_candle)
        for peak in peaks:
            self.chart.draw_rectangle(start_x=peak.name,
                                      start_y=peak['Low'],
                                      end_x=peak.name + 200,
                                      end_y=peak['High'],
                                      opacity=0.2)

        if self.order_handler.position is not None:
            return None, self.chart.chart, self.mongo_chart_id

        for peak in peaks:
            if peak['Low'] <= current_candle['Low'] <= peak['High'] < previous_candle['Low'] and (
                    current_candle.name - peak.name) <= 200:
                stop_loss = peak['Low'] - current_candle['atr'] / 2
                target_price = current_candle['Close'] + (current_candle['Close'] - stop_loss) * self.rtr_ratio

                if ((stop_loss / peak['High']) - 1) > self.max_stop_loss:
                    stop_loss = peak['High'] * (1 - self.max_stop_loss)
                    print(f'{current_candle.name} was over limit')

                self.order_handler.open_position(order_type='long',
                                                 buy_candle=current_candle,
                                                 target_price=target_price,
                                                 stop_loss=stop_loss,
                                                 info=True)

            elif previous_candle['High'] < peak['Low'] <= current_candle['High'] <= peak['High'] and (
                    current_candle.name - peak.name) <= 200:
                stop_loss = peak['High'] + current_candle['atr'] / 2
                target_price = current_candle['Close'] - (stop_loss - current_candle['Close']) * self.rtr_ratio

                if ((peak['Low'] / stop_loss) - 1) > self.max_stop_loss:
                    stop_loss = peak['Low'] * (1 - self.max_stop_loss)
                    print(f'{current_candle.name} was over limit')

                self.order_handler.open_position(order_type='short',
                                                 buy_candle=current_candle,
                                                 target_price=target_price,
                                                 stop_loss=stop_loss,
                                                 info=True)



        return None, self.chart.chart, self.mongo_chart_id

    def previous_candle(self, n=0):
        # Ha n=0 akkor az a legújabb candlet jelenti
        return self.data15m.iloc[len(self.data15m) - n - 1]


# --------------------------------------------------------------------------


strategy_holder = []
config = configparser.ConfigParser()
config.read('support_and_resistance_config.ini')

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
                                    max_stop_loss=float(config['SETTINGS']['max_stop_loss']),
                                    atr_multiplier=float(config['SETTINGS']['atr_multiplier']),
                                    rtr_ratio=float(config['SETTINGS']['rtr_ratio'])))

print(f'\nRunning strategy (support_and_resistance) on symbols: {symbols}\n')


while True:
    time.sleep(sleep_time)
    start = time.time()
    for strategy in strategy_holder:
        result = strategy.run_strategy()
        mongo.add_chart_to_db(strategy.symbol, result[1], strategy.strategy_name, result[2])

    if show_runtime:
        print(f'Strategy ran on all symbols in {time.time() - start}s')
