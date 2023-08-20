import random

import mongo
from strategies_live import OrderHandlerLive
import pandas as pd


class strategy:
    def __init__(self, symbol: str, start_data):
        self.symbol = symbol.upper()
        self.strategy_name = 'random_strategy'
        self.mongo_chart_id = 1
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
                mongo.update_pnl(self.order_handler.position, self.data15m.iloc[len(self.data15m) - 1])
        except:
            return

    def run_strategy(self, data):
        self.update_data(data)
        current_candle = self.previous_candle()
        self.order_handler.check_position(current_candle)
        if self.order_handler.position is not None:
            return None, self.chart.chart, self.mongo_chart_id

        rand = random.randint(1, 2)

        if rand == 1:
            self.order_handler.open_position(order_type='long',
                                             buy_candle=current_candle,
                                             info=True,
                                             target_price=current_candle['Close'] * 1.04,
                                             stop_loss=current_candle['Close'] * 0.98)
        else:
            self.order_handler.open_position(order_type='short',
                                             buy_candle=current_candle,
                                             info=True,
                                             target_price=current_candle['Close'] * 0.96,
                                             stop_loss=current_candle['Close'] * 1.02)

        return None, self.chart.chart, self.mongo_chart_id

    def previous_candle(self, n=0):
        return self.data15m.iloc[len(self.data15m) - n - 1]
