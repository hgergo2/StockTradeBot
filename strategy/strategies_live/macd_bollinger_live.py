import mongo
from strategies_live import OrderHandlerLive
import pandas as pd
import pandas_ta as ta


class strategy:
    def __init__(self, symbol: str, start_data):
        self.symbol = symbol.upper()
        self.strategy_name = 'macd_bollinger'
        self.mongo_chart_id = 3
        self.data15m = None
        self.update_data(start_data)
        self.order_handler = OrderHandlerLive.OrderHandlerLive(self.symbol, '15m', self.data15m, self.strategy_name,
                                                               create_chart_subplot=True)
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

    def run_strategy(self, data, rtr_ratio=2, atr_multiplier=2):
        self.update_data(data)
        current_candle = self.previous_candle()
        previous_candle = self.previous_candle(1)
        self.order_handler.check_position(current_candle)
        if self.order_handler.position is not None:
            return None, self.chart.chart, self.mongo_chart_id

        if previous_candle['macd_hist'] > previous_candle['bb_lower'] and current_candle['macd_hist'] < current_candle['bb_lower']:
            stop_loss = current_candle['Close'] + (current_candle['atr'] * atr_multiplier)
            target_price = current_candle['Close'] - (stop_loss - current_candle['Close']) * rtr_ratio

            self.order_handler.open_position(order_type='short',
                                             buy_candle=current_candle,
                                             target_price=target_price,
                                             stop_loss=stop_loss,
                                             info=True)
        elif previous_candle['macd_hist'] < previous_candle['bb_upper'] and current_candle['macd_hist'] > current_candle['bb_upper']:
            stop_loss = current_candle['Close'] - (current_candle['atr'] * atr_multiplier)
            target_price = current_candle['Close'] + (current_candle['Close'] - stop_loss) * rtr_ratio

            self.order_handler.open_position(order_type='long',
                                             buy_candle=current_candle,
                                             target_price=target_price,
                                             stop_loss=stop_loss,
                                             info=True)

        return None, self.chart.chart, self.mongo_chart_id

    def previous_candle(self, n=0):
        return self.data15m.iloc[len(self.data15m) - n - 1]
