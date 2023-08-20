import Position
import stockData as sd
#import indicators as ind
import OrderHandler as oh
import pandas_ta as ta


def get_index_by_date_hour(data, date, start_from=0):
    for i in range(start_from, len(data)):
        if str(data.iloc[i]['DateTime'])[:13] == str(date)[:13]:
            return i


class strategy:
    def __init__(self, symbol: str, is_live: bool, ema_offset_multiplier=1.5):
        symbol.upper()
        self.is_live = is_live
        self.strategy_name = '200ema'
        self.symbol = symbol
        if is_live:
            self.data15m = sd.get_data(symbol, '15m', '20d')
            self.data30m = sd.get_data(symbol, '30m', '40d')
            self.data60m = sd.get_data(symbol, '60m', '50d')
        elif not is_live:
            self.data15m = sd.get_data(symbol, '15m', '60d')
            self.data30m = sd.get_data(symbol, '30m', '60d')
            self.data60m = sd.get_data(symbol, '60m', '60d')

        self.data15m['atr'] = ta.atr(self.data15m['High'], self.data15m['Low'], self.data15m['Close'])
        self.data15m['ema200'] = ta.ema(self.data15m['Close'], length=200)
        self.data30m['ema200'] = ta.ema(self.data30m['Close'], length=200)
        self.data60m['ema200'] = ta.ema(self.data60m['Close'], length=200)

        self.order_handler = oh.OrderHandler(self.data15m, symbol)
        self.ch = self.order_handler.ch
        self.ch.add_moving_line(data=self.data15m['ema200'], color='blue', width=1, name='ema200')

        self.test_ema_offset_upper = []
        self.test_ema_offset_lower = []
        for a in range(len(self.data15m)):
            self.test_ema_offset_upper.append(
                self.data15m.iloc[a]['ema200'] + self.data15m.iloc[a]['atr'] * ema_offset_multiplier)
            self.test_ema_offset_lower.append(
                self.data15m.iloc[a]['ema200'] - self.data15m.iloc[a]['atr'] * ema_offset_multiplier)

        self.ch.add_moving_line(data=self.test_ema_offset_upper, color='orange', width=1, name='ema200 upper')
        self.ch.add_moving_line(data=self.test_ema_offset_lower, color='orange', width=1, name='ema200 lower')

        #self.data30mchart = chartHandler.ChartHandlerBacktest(self.data30m, symbol)
        #self.data30mchart.add_moving_line(self.data30m['ema200'], 'blue', 1, '200ema')
        #self.data30mchart.chart.show()
#
        #self.data60mchart = chartHandler.ChartHandlerBacktest(self.data60m, symbol)
        #self.data60mchart.add_moving_line(self.data60m['ema200'], 'blue', 1, '200ema')
        #self.data60mchart.chart.show()

    def run_strategy(self, show_chart=True, max_stop_loss=0.03):
        under_ema = True
        if self.data15m.iloc[200]['Close'] < self.data15m.iloc[200]['ema200'] * 0.99:
            under_ema = True
        else:
            under_ema = False

        def check_position():
            if self.order_handler.position is not None:
                previous_candle = self.data15m.iloc[index - 1]
                if self.order_handler.position.is_long:
                    if previous_candle['Close'] > self.test_ema_offset_lower[index-1] and \
                            current_candle['Close'] < self.test_ema_offset_lower[index]:
                        self.order_handler.sell(current_candle, 'Close')
                elif not self.order_handler.position.is_long:
                    if previous_candle['Close'] < self.test_ema_offset_upper[index-1] and \
                            current_candle['Close'] > self.test_ema_offset_upper[index]:
                        self.order_handler.sell(current_candle, 'Close')

        for index in range(200, len(self.data15m) - 1):
            current_candle = self.data15m.iloc[index]
            current_candle_30m = self.data30m.iloc[round(index / 2)]
            m60_index = get_index_by_date_hour(self.data60m,
                                               self.data30m.iloc[round(index / 2)]['DateTime'],
                                               start_from=round(index / 4))
            if m60_index is not None:
                current_candle_60m = self.data60m.iloc[m60_index]
            else:
                #print(f'Index is None at {index}')
                continue
            #self.order_handler.check_position(current_candle)
            check_position()
            if current_candle_30m['ema200'] < current_candle_30m['Close'] and \
                    current_candle_60m['ema200'] < current_candle_60m['Close']:

                if current_candle['Close'] < self.test_ema_offset_lower[index]:
                    under_ema = True
                elif current_candle['Close'] > self.test_ema_offset_upper[index]:
                    if under_ema:
                        stop_loss = current_candle['ema200'] - current_candle['atr']
                        if stop_loss < current_candle['Close'] * (1 - max_stop_loss):
                            stop_loss = current_candle['Close'] * (1 - max_stop_loss)
                            # print(f'Stop loss over threshold, new stop loss: {stop_loss}')
                        target_price = current_candle['Close'] + (current_candle['Close'] - stop_loss) * 2
                        self.order_handler.open_position(is_long=True,
                                                         candle=current_candle,
                                                         info=True)
                    under_ema = False
            if current_candle_30m['ema200'] > current_candle_30m['Close'] and \
                    current_candle_60m['ema200'] > current_candle_60m['Close']:

                if current_candle['Close'] < self.test_ema_offset_lower[index]:
                    if not under_ema:
                        stop_loss = current_candle['ema200'] + current_candle['atr']
                        if stop_loss > current_candle['Close'] * (1 + max_stop_loss):
                            stop_loss = current_candle['Close'] * (1 + max_stop_loss)
                            # print(f'Stop loss over threshold, new stop loss: {stop_loss}')
                        target_price = current_candle['Close'] - (stop_loss - current_candle['Close']) * 2

                        self.order_handler.open_position(is_long=False,
                                                         candle=current_candle,
                                                         info=True)
                    under_ema = True
                elif current_candle['Close'] > self.test_ema_offset_upper[index]:
                    under_ema = False

        if self.order_handler.position is not None:
            last_candle = self.data15m.iloc[len(self.data15m) - 1]
            #self.order_handler.sell(self.data15m.iloc[len(self.data15m)-1], 'Close')
            if self.order_handler.position.is_long:
                if last_candle['Close'] > self.order_handler.position.buy_price:
                    self.ch.draw_position(Position.Position(is_long=self.order_handler.position.is_long,
                                                            index=self.order_handler.position.index,
                                                            target_price=last_candle['Close'],
                                                            stop_loss=self.order_handler.position.buy_price,
                                                            buy_price=self.order_handler.position.buy_price,
                                                            symbol=self.order_handler.symbol
                                                            ), len(self.data15m))
                elif last_candle['Close'] < self.order_handler.position.buy_price:
                    self.ch.draw_position(Position.Position(is_long=self.order_handler.position.is_long,
                                                            index=self.order_handler.position.index,
                                                            target_price=self.order_handler.position.buy_price,
                                                            stop_loss=last_candle['Close'],
                                                            buy_price=self.order_handler.position.buy_price,
                                                            symbol=self.order_handler.symbol
                                                            ), len(self.data15m))
            elif not self.order_handler.position.is_long:
                if last_candle['Close'] > self.order_handler.position.buy_price:
                    self.ch.draw_position(Position.Position(is_long=False,
                                                            index=self.order_handler.position.index,
                                                            target_price=self.order_handler.position.buy_price,
                                                            stop_loss=last_candle['Close'],
                                                            buy_price=self.order_handler.position.buy_price,
                                                            symbol=self.order_handler.symbol
                                                            ), len(self.data15m))
                elif last_candle['Close'] < self.order_handler.position.buy_price:
                    self.ch.draw_position(Position.Position(is_long=False,
                                                            index=self.order_handler.position.index,
                                                            target_price=last_candle['Close'],
                                                            stop_loss=self.order_handler.position.buy_price,
                                                            buy_price=self.order_handler.position.buy_price,
                                                            symbol=self.order_handler.symbol
                                                            ), len(self.data15m))

        if show_chart and not self.is_live:
            self.ch.chart.show()
        return self.order_handler.get_statistics(), self.ch.chart
