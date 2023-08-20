import stockData as sd
import OrderHandler as oh
import pandas_ta as ta
# szar szar szar szar szar szar szar szar


class strategy:
    def __init__(self, symbol: str):
        symbol.upper()
        timeframe = '1d'
        self.data15m = sd.get_data(symbol, timeframe, '1000d')
        self.data15m['ema'] = ta.ema(close=self.data15m['Close'], length=20)
        self.data15m['adx'] = ta.adx(high=self.data15m['High'], low=self.data15m['Low'], close=self.data15m['Close'], length=14).iloc[:, 0]

        self.order_handler = oh.OrderHandler(self.data15m, symbol, timeframe=timeframe)
        self.ch = self.order_handler.ch

        self.ch.add_subplot(self.data15m['adx'], type='line')
        self.ch.add_moving_line(data=self.data15m['ema'], color='blue', width=1, name='ema20')

    def run_strategy(self, show_chart=True, max_stop_loss=0.03, adx_min=30):
        possible_long = None
        possible_short = None
        def check_position():
            if self.order_handler.position is not None:
                if self.order_handler.position.is_long:
                    if current_candle['Close'] < current_candle['ema']:
                        self.order_handler.sell(current_candle, 'Close')
                elif not self.order_handler.position.is_long:
                    if current_candle['Close'] > current_candle['ema']:
                        self.order_handler.sell(current_candle, 'Close')

        for n in range(21, len(self.data15m)-1):
            current_candle = self.data15m.iloc[n]
            previous_candle = self.data15m.iloc[n-1]
            check_position()
            if possible_long is not None:
                if current_candle['Low'] < current_candle['ema']:
                    possible_long = None
                elif current_candle['Close'] > possible_long['High']:
                    # open long
                    self.order_handler.open_position(is_long=True,
                                                     candle=current_candle,
                                                     stop_loss=possible_long['Low'],
                                                     info=False)
                    possible_long = None
            elif possible_short is not None:
                if current_candle['Close'] < possible_short['Low']:
                    self.order_handler.open_position(is_long=False,
                                                     candle=current_candle,
                                                     stop_loss=possible_short['Low'],
                                                     info=False)
                    possible_short = None

            if current_candle['adx'] > adx_min:
                if current_candle['Low'] < current_candle['ema'] < current_candle['Close']:
                    possible_short = None
                    possible_long = current_candle

                elif current_candle['High'] > current_candle['ema'] > current_candle['Close']:
                    possible_long = None
                    possible_short = current_candle

        if show_chart:
            self.ch.chart.show()
        return self.order_handler.get_statistics()
