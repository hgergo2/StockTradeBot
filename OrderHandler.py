import pandas as pd
import Position
import chartHandler
import statisticsInfo


class OrderHandler:

    def __init__(self, full_data, symbol: str, timeframe=''):
        self.symbol = symbol
        self.full_data = full_data
        self.position = None
        self.wins = 0
        self.losses = 0
        self.all_trades = []
        self.ch = chartHandler.ChartHandlerBacktest(self.full_data, symbol, timeframe=timeframe)

    def open_position(self, is_long: bool, candle, target_price=0, stop_loss=0, info=True):
        if self.position is None:
            self.position = Position.Position(is_long=is_long,
                                              target_price=target_price,
                                              stop_loss=stop_loss,
                                              index=candle.name,
                                              buy_price=candle['Close'],
                                              symbol=self.symbol)
            if is_long and info:
                print(f'Opened [Long] position at index: {self.position.index}')
            elif not is_long and info:
                print(f'Opened [Short] position at index: {self.position.index}')

    def check_position(self, candle):
        #1 = win | 0 = lose | -1 = semmi
        if self.position is not None:
            if self.position.is_long:
                self.position.trade_length += 1
                if candle['High'] >= self.position.target_price:
                    self.__add_win(candle)
                    return 1
                elif candle['Low'] <= self.position.stop_loss:
                    self.__add_lose(candle)
                    return 0
                return -1
            elif not self.position.is_long:
                self.position.trade_length += 1
                if candle['High'] >= self.position.stop_loss:
                    self.__add_lose(candle)
                    return 0
                elif candle['Low'] <= self.position.target_price:
                    self.__add_win(candle)
                    return 1
                return -1

    def sell(self, sell_candle, candle_type: str):
        if self.position is None:
            return
        candle_type[0].upper()
        if self.position.is_long:
            if sell_candle[candle_type] > self.position.buy_price:
                # Long win
                self.position.target_price = sell_candle[candle_type]
                self.position.stop_loss = self.position.buy_price
                self.__add_win(sell_candle)
            elif sell_candle[candle_type] < self.position.buy_price:
                # Long lose
                self.position.target_price = self.position.buy_price
                self.position.stop_loss = sell_candle[candle_type]
                self.__add_lose(sell_candle)

        elif not self.position.is_long:
            if sell_candle[candle_type] < self.position.buy_price:
                # Short win
                self.position.target_price = sell_candle[candle_type]
                self.position.stop_loss = self.position.buy_price
                self.__add_win(sell_candle)
            elif sell_candle[candle_type] > self.position.buy_price:
                # Short lose
                self.position.stop_loss = sell_candle[candle_type]
                self.position.target_price = self.position.buy_price
                self.__add_lose(sell_candle)

    def __add_win(self, candle):
        self.wins += 1
        self.position.is_win = True
        self.position.profit = self.__calc_profit()
        self.position.trade_length = candle.name - self.position.index
        self.ch.draw_position(self.position, candle.name)
        self.all_trades.append(self.position)
        self.position = None

    def __add_lose(self, candle):
        self.losses += 1
        self.position.is_win = False
        self.position.profit = self.__calc_profit()
        self.position.trade_length = candle.name - self.position.index
        self.ch.draw_position(self.position, candle.name)
        self.all_trades.append(self.position)
        self.position = None

    def get_statistics(self):
        return statisticsInfo.Stats(self.all_trades, self.symbol)

    def __calc_profit(self):
        #print((self.position.target_price / self.position.buy_price) - 1)
        if self.position.is_long:
            if self.position.is_win:
                return (self.position.target_price / self.position.buy_price) - 1
            else:
                return -abs((self.position.stop_loss / self.position.buy_price) - 1)
        else:
            if self.position.is_win:
                return abs((self.position.target_price / self.position.buy_price) - 1)
            else:
                return -abs((self.position.stop_loss / self.position.buy_price) - 1)
