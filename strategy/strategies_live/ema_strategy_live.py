import time
import pandas as pd
import pandas_ta as ta
from strategies_live import OrderHandlerLive
import mongo
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)


def get_index_by_date_hour(data, date, start_from=0):
    for i in range(start_from, len(data)):
        if str(data.iloc[i]['DateTime'])[:13] == str(date)[:13]:
            return i


def calculate_top_and_bottom(data, ema_offset_multiplier):
    top, bottom = [], []
    for a in range(len(data)):
        top.append(data.iloc[a]['ema200'] + data.iloc[a]['atr'] * ema_offset_multiplier)
        bottom.append(data.iloc[a]['ema200'] - data.iloc[a]['atr'] * ema_offset_multiplier)
    return top, bottom


class strategy:
    def __init__(self, symbol: str, start_data, start_data_30m, start_data_60m, ema_offset_multiplier=1.5, max_stop_loss=0.03):
        symbol.upper()
        self.symbol = symbol
        self.strategy_name = '200ema_strategy'
        self.ema_offset_multiplier = ema_offset_multiplier
        self.max_stop_loss = max_stop_loss
        self.mongo_chart_id = 0
        self.data15m = None
        self.data30m = None
        self.data60m = None
        self.under_ema = None
        self.update_data(start_data, start_data_30m, start_data_60m)
        self.order_handler = OrderHandlerLive.OrderHandlerLive(self.symbol, '15m', self.data15m, self.strategy_name)
        self.chart = self.order_handler.chart

    def get_ema_over_or_under(self):
        for a in range(200, len(self.data15m) - 1):
            if self.data15m.iloc[a]['Close'] < self.data15m.iloc[a]['bottom']:
                self.under_ema = True
            elif self.data15m.iloc[a]['Close'] > self.data15m.iloc[a]['top']:
                self.under_ema = False

    def update_data(self, data, data_30m, data_60m):
        if data is None: return
        start = time.time()
        try:

            self.data15m = pd.DataFrame({'Open': data['Open'][self.symbol],
                                         'High': data['High'][self.symbol],
                                         'Low': data['Low'][self.symbol],
                                         'Close': data['Close'][self.symbol],
                                         'Volume': data['Volume'][self.symbol],
                                         'DateTime': data['DateTime']})
            if self.order_handler.position is not None:
                mongo.update_pnl(self.order_handler.position, self.data15m.iloc[len(self.data15m) - 1])
            self.data15m['ema200'] = ta.ema(self.data15m['Close'], length=200)
            self.data15m['atr'] = ta.atr(self.data15m['High'], self.data15m['Low'], self.data15m['Close'])
            self.data15m['top'], self.data15m['bottom'] = calculate_top_and_bottom(self.data15m, self.ema_offset_multiplier)

            self.data30m = pd.DataFrame({'Open': data_30m['Open'][self.symbol],
                                         'High': data_30m['High'][self.symbol],
                                         'Low': data_30m['Low'][self.symbol],
                                         'Close': data_30m['Close'][self.symbol],
                                         'Volume': data_30m['Volume'][self.symbol],
                                         'DateTime': data_30m['DateTime']})

            self.data60m = pd.DataFrame({'Open': data_60m['Open'][self.symbol],
                                         'High': data_60m['High'][self.symbol],
                                         'Low': data_60m['Low'][self.symbol],
                                         'Close': data_60m['Close'][self.symbol],
                                         'Volume': data_60m['Volume'][self.symbol],
                                         'DateTime': data_60m['DateTime']})

            self.data30m['ema200'] = ta.ema(self.data30m['Close'], length=200)
            self.data60m['ema200'] = ta.ema(self.data60m['Close'], length=200)
        except:
            pass
        try:
            if self.chart is not None:
                self.chart.update_chart(self.data15m)
                self.chart.add_moving_line(self.data15m['ema200'], color='blue', width=1, name='200ema')
                self.chart.add_moving_line(self.data15m['top'], color='orange', width=1, name='top')
                self.chart.add_moving_line(self.data15m['bottom'], color='orange', width=1, name='bottom')
        except:
            pass
        #print(f'Data update time: {time.time() - start}')

    def run_strategy(self, data, data_30m, data_60m):
        start = time.time()
        self.update_data(data, data_30m, data_60m)
        start_no_update = time.time()
        if self.under_ema is None:
            self.get_ema_over_or_under()
        current_candle = self.previous_candle()
        previous_candle = self.previous_candle(1)

        def check_position():
            if self.order_handler.position is not None:
                if self.order_handler.position.order_type == 'long' and current_candle['Close'] < current_candle['bottom']:
                        print(f'Closing position on {self.symbol} strategy: {self.strategy_name}')
                        self.order_handler.close_position(current_candle)

                elif self.order_handler.position.order_type == 'short' and current_candle['Close'] > current_candle['top']:
                        print(f'Closing position on {self.symbol} strategy: {self.strategy_name}')
                        self.order_handler.close_position(current_candle)

        current_candle_30m = self.data30m.iloc[len(self.data30m)-1]
        current_candle_60m = self.data60m.iloc[len(self.data60m)-1]
        check_position()
        if self.order_handler.position is not None:
            return None, self.chart.chart, self.mongo_chart_id
        if current_candle_30m['ema200'] < current_candle_30m['Close'] and \
            current_candle_60m['ema200'] < current_candle_60m['Close']:

            if current_candle['Close'] < current_candle['bottom']:
                self.under_ema = True
            elif current_candle['Close'] > current_candle['top'] and self.under_ema:
                if self.under_ema:
                    stop_loss = current_candle['ema200'] - current_candle['atr']
                    if stop_loss < current_candle['Close'] * (1 - self.max_stop_loss):
                        stop_loss = current_candle['Close'] * (1 - self.max_stop_loss)
                    self.order_handler.open_position(order_type='long',
                                                     buy_candle=current_candle,
                                                     info=True)
                    self.under_ema = False

        if current_candle_30m['ema200'] > current_candle['Close'] and \
            current_candle_60m['ema200'] > current_candle['Close']:

            if current_candle['Close'] < current_candle['bottom']:
                if not self.under_ema:
                    stop_loss = current_candle['ema200'] - current_candle['atr']
                    if stop_loss < current_candle['Close'] * (1 - self.max_stop_loss):
                        stop_loss = current_candle['Close'] * (1 - self.max_stop_loss)
                    self.order_handler.open_position(order_type='short',
                                                     buy_candle=current_candle,
                                                     info=True)
        #print(f'Strategy ran in {time.time() - start} without update time: {time.time() - start_no_update}')

        return None, self.chart.chart, self.mongo_chart_id

    def previous_candle(self, n=0):
        # Ha n=0 akkor az a legújabb candlet jelenti
        return self.data15m.iloc[len(self.data15m) - n - 1]
