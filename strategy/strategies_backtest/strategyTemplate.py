import stockData as sd
import OrderHandler as oh
import pandas_ta as ta

class strategy:
    def __init__(self, symbol: str, ema_offset_multiplier=1.5):
        symbol.upper()
        timeframe = '15m'
        self.data15m = sd.get_data(symbol, timeframe, '60d')

        self.order_handler = oh.OrderHandler(self.data15m, symbol, timeframe=timeframe)
        self.ch = self.order_handler.ch

    def run_strategy(self, show_chart=True, max_stop_loss=0.03):

        for n in range(len(self.data15m)):
            pass

        if show_chart:
            self.ch.chart.show()
        return self.order_handler.get_statistics()
