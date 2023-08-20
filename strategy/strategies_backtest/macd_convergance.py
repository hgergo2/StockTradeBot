import stockData as sd
import OrderHandler as oh
import pandas_ta as ta

class strategy:
    def __init__(self, symbol: str, ema_offset_multiplier=1.5):
        symbol.upper()
        timeframe = '15m'
        self.data15m = sd.get_data(symbol, timeframe, '60d')
        macd = ta.macd(self.data15m['Close'])
        self.data15m['macd_fast'], self.data15m['macd_hist'], self.data15m['macd_slow'] = macd['MACD_12_26_9'], macd['MACDh_12_26_9'], macd['MACDs_12_26_9']

        self.order_handler = oh.OrderHandler(self.data15m, symbol, timeframe=timeframe)
        self.ch = self.order_handler.ch

        self.ch.add_subplot(self.data15m['macd_fast'], type='line')
        self.ch.add_subplot_data(self.data15m['macd_slow'], type='line')
        self.ch.add_subplot_data(self.data15m['macd_hist'], type='bar')

    def run_strategy(self, show_chart=True, max_stop_loss=0.03):

        for n in range(34, len(self.data15m)):
            current_candle = self.data15m.iloc[n]
            previous_candle = self.data15m.iloc[n-1]
            peak_candle = None
            went_below = None

            if current_candle['macd_hist'] > previous_candle['macd_hist'] and current_candle['macd_hist'] > 0:
                print(f'Found peak candle at: {n}')
                peak_candle = current_candle
            if current_candle['macd_hist'] < 0:
                print(f'Went below at: {n}')
                went_below = True
            if went_below and current_candle['macd_hist'] > 0 and previous_candle['macd_hist'] > current_candle['mach_hist'] and \
               previous_candle['macd_hist'] < peak_candle['macd_hist'] and peak_candle['Close'] < previous_candle['Close']:
                    self.ch.draw_line(peak_candle.name, peak_candle['Close'], previous_candle.name, previous_candle['Close'])
                    print('asdasdasddasasddsaads')
                    peak_candle = None
                    went_below = None




        if show_chart:
            self.ch.chart.show()
        return self.order_handler.get_statistics()
