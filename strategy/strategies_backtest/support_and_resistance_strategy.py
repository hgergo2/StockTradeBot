import stockData as sd
import OrderHandler as oh
import pandas_ta as ta


class strategy:
    def __init__(self, symbol: str, timeframe='15m', ema_offset_multiplier=1.5):
        symbol.upper()
        self.data15m = sd.get_data(symbol, timeframe, '60d')
        self.data15m['atr'] = ta.atr(self.data15m['High'], self.data15m['Low'], self.data15m['Close'])
        self.data15m['avg_volume'] = ta.ma('sma', self.data15m['Volume'])
        self.order_handler = oh.OrderHandler(self.data15m, symbol, timeframe=timeframe)
        self.ch = self.order_handler.ch

        self.ch.add_subplot(self.data15m['Volume'], type='bar')
        self.ch.add_subplot_data(self.data15m['avg_volume'], type='line', color='red')

    def run_strategy(self, show_chart=True, max_stop_loss=0.03, atr_multiplier=4):
        peaks_short = self.calc_short_zones(atr_multiplier)
        peaks_long = self.calc_long_zones(atr_multiplier)

        for peak in peaks_long:
            self.ch.draw_rectangle(start_x=peak.name,
                                   start_y=peak['Low'],
                                   end_x=peak.name+100,
                                   end_y=peak['High'],
                                   fillcolor='green',
                                   color='green',
                                   opacity=0.4)
        for peak in peaks_short:
            self.ch.draw_rectangle(start_x=peak.name,
                                   start_y=peak['Low'],
                                   end_x=peak.name+100,
                                   end_y=peak['High'],
                                   fillcolor='red',
                                   color='red',
                                   opacity=0.4)

        if show_chart:
            self.ch.chart.show()

        #return self.order_handler.get_statistics(), self.ch.chart
        return None, self.ch.chart

    def calc_short_zones(self, atr_multiplier):

        peaks = []
        current_peak_long = None
        for n in range(35, len(self.data15m)):
            current_candle = self.data15m.iloc[n]
            previous_candle = self.data15m.iloc[n - 1]

            if current_peak_long is None and previous_candle['Close'] > previous_candle['Open']:
                current_peak_long = current_candle
            if current_peak_long is not None:
                if current_candle['Close'] > current_peak_long['Close'] and previous_candle['Close'] > previous_candle['Open']:
                    current_peak_long = current_candle
                elif current_peak_long['Close'] - (current_peak_long['atr'] * atr_multiplier) > current_candle['Close'] > \
                        self.data15m.iloc[n - 5]['Close']:
                    peaks.append(current_peak_long)
                    current_peak_long = None

        return peaks

    def calc_long_zones(self, atr_multiplier):
        peaks = []
        current_peak_short = None

        for n in range(35, len(self.data15m)):
            current_candle = self.data15m.iloc[n]
            previous_candle = self.data15m.iloc[n - 1]

            if current_peak_short is None and previous_candle['Close'] < previous_candle['Open']:
                current_peak_short = current_candle
            if current_peak_short is not None:
                if current_candle['Close'] < current_peak_short['Close'] and previous_candle['Close'] < previous_candle['Open']:
                    current_peak_short = current_candle
                elif current_peak_short['Close'] + (current_peak_short['atr'] * atr_multiplier) < current_candle['Close'] < \
                        self.data15m.iloc[n - 5]['Close']:
                    peaks.append(current_peak_short)
                    current_peak_short = None

        return peaks


