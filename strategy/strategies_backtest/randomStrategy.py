import random

import stockData as sd
import OrderHandler as oh


class strategy:
    def __init__(self, symbol: str, ema_offset_multiplier=1.5):
        symbol.upper()
        self.data15m = sd.get_data(symbol, '15m', '60d')


        self.order_handler = oh.OrderHandler(self.data15m, symbol)
        self.ch = self.order_handler.ch


    def run_strategy(self, show_chart=True, max_stop_loss=0.03):

        for n in range(len(self.data15m)):
            current_candle = self.data15m.iloc[n]
            self.order_handler.check_position(current_candle)
            rand = random.randint(1, 2)
            # 1 = long | 2 = short

            if rand is 1:
                self.order_handler.open_position(is_long=True,
                                                 candle=current_candle,
                                                 target_price=current_candle['Close'] * 1.03,
                                                 stop_loss=current_candle['Close'] * 0.985)
            else:
                self.order_handler.open_position(is_long=False,
                                                 candle=current_candle,
                                                 target_price=current_candle['Close'] * 0.97,
                                                 stop_loss=current_candle['Close'] * 1.015)


        if show_chart:
            self.ch.chart.show()
        return self.order_handler.get_statistics()
