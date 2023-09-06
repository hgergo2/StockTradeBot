import pandas as pd
import pandas_ta as ta
from strategies_live import OrderHandlerLive
import mongo
import time


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
    def __init__(self, symbol: str, start_data):
        self.symbol = symbol.upper()
        self.strategy_name = 'support_and_resistance'
        self.mongo_chart_id = 2

        self.data15m = None
        self.update_data(start_data)
        self.order_handler = OrderHandlerLive.OrderHandlerLive(self.symbol, '15m', self.data15m, self.strategy_name)
        self.chart = self.order_handler.chart

    def update_data(self, data):
        if data is None: return

        try:
            self.data15m = pd.DataFrame({'Open': data['Open'][self.symbol],
                                         'High': data['High'][self.symbol],
                                         'Low': data['Low'][self.symbol],
                                         'Close': data['Close'][self.symbol],
                                         'Volume': data['Volume'][self.symbol],
                                         'DateTime': data['DateTime']})
            self.chart.update_chart(self.data15m)
            if self.order_handler.position is not None:
                mongo.update_pnl(self.order_handler.position, self.data15m.iloc[len(self.data15m)-1])

            self.data15m['atr'] = ta.atr(self.data15m['High'], self.data15m['Low'], self.data15m['Close'])
            self.data15m['avg_volume'] = ta.ma('sma', self.data15m['Volume'])


        except:
            return

    def run_strategy(self, data, max_stop_loss=0.03, atr_multiplier=4, rtr_ratio=3):
        self.update_data(data)
        #__peaks_short = calc_short_zones(self.data15m[-200:], atr_multiplier)
        #__peaks_long = calc_short_zones(self.data15m[-200:], atr_multiplier)
        #print(self.data15m[-500:].to_string())
        peaks = calc_zones(self.data15m[-200:], atr_multiplier)

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
                target_price = current_candle['Close'] + (current_candle['Close'] - stop_loss) * rtr_ratio

                if ((stop_loss / peak['High']) - 1) > max_stop_loss:
                    stop_loss = peak['High'] * (1 - max_stop_loss)
                    print(f'{current_candle.name} was over limit')

                self.order_handler.open_position(order_type='long',
                                                 buy_candle=current_candle,
                                                 target_price=target_price,
                                                 stop_loss=stop_loss,
                                                 info=True)

            elif previous_candle['High'] < peak['Low'] <= current_candle['High'] <= peak['High'] and (
                    current_candle.name - peak.name) <= 200:
                stop_loss = peak['High'] + current_candle['atr'] / 2
                target_price = current_candle['Close'] - (stop_loss - current_candle['Close']) * rtr_ratio

                if ((peak['Low'] / stop_loss) - 1) > max_stop_loss:
                    stop_loss = peak['Low'] * (1 - max_stop_loss)
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
