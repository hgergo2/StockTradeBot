import Position
import pandas as pd


class Stats:

    def __init__(self, position: [Position.Position], symbol: str):
        self.symbol = symbol
        self.__positions = position
        self.positions = self.__convert_positions_to_dataframe()
        print(self.positions.to_string())
        self.wins = self.__calc_wins()
        self.losses = self.__calc_losses()
        self.winrate = self.__calc_winrate()
        self.winratio = self.__calc_winratio()
        self.longest_trade = self.__calc_longest_trade()
        self.gain = self.__calc_gain()

    def __convert_positions_to_dataframe(self):
        df = pd.DataFrame({'is_long': [bool], 'target_price': [float], 'stop_loss': [float], 'index': [int], 'buy_price': [float],
                                       'symbol': [str], 'trade_length': [int], 'is_win': [bool], 'profit': [float]})
        for count, i in enumerate(self.__positions):
            df.loc[count] = [i.is_long, i.target_price, i.stop_loss, i.index, i.buy_price,
                                   i.symbol, i.trade_length, i.is_win, i.profit]

        return df

    def __calc_winratio(self):
        if self.losses > 0:
            return self.wins / self.losses
        return 0

    def __calc_winrate(self):
        if self.losses + self.wins > 0:
            return self.wins / (self.wins + self.losses)
        else:
            return 0

    def __calc_longest_trade(self):
        return max(self.positions['trade_length'])

    def __calc_losses(self):
        sum = 0
        for pos in self.__positions:
            if not pos.is_win:
                sum += 1
        return sum

    def __calc_wins(self):
        sum  = 0
        for pos in self.__positions:
            if pos.is_win:
                sum += 1
        return sum

    def __calc_gain(self):
        return self.positions['profit'].sum() * 100

    def show_statistics(self):
        print(f'\n====={self.symbol}=====\n'
              f'Wins: {self.wins}\n'
              f'Losses: {self.losses}\n'
              f'Winratio: {self.winratio}\n'
              f'Winrate [%]: {"{:.2f}".format(self.winrate * 100)}\n'
              f'Gain [%]: {"{:.2f}".format(self.gain)}\n'
              f'Longest trade [Candle]: {self.longest_trade}\n'
              f'Number of trades: {len(self.__positions)}\n')


class StatsSummary:

    def __init__(self):
        self.stats = pd.DataFrame({'symbol': [str], 'wins': [int], 'losses': [int], 'winratio': [float],
                                   'winrate': [float], 'gain': [float], 'longest_trade': [int], 'number_of_trades': [int]})
        self.indx = 0

    def add(self, st: Stats):
        self.stats.loc[self.indx] = [str(st.symbol), int(st.wins), int(st.losses), float(st.winratio), float(st.winrate),
                                           float(st.gain), int(st.longest_trade), int(len(st.positions))]
        self.indx += 1

    def show_stats(self):
        print(f'\n========Summary========\n'
              f'wins: {self.sum_wins()}\n'
              f'losses: {self.sum_losses()}\n'
              f'gain [%]: {"{:.2f}".format(self.sum_gain())}\n'
              f'average winrate [%]: {"{:.2f}".format(self.avg_winrate() * 100)}\n'
              f'longest trade: {self.longest_trade()}\n'
              f'average number of trades: {"{:.2f}".format(self.avg_number_of_trades())}\n')

    def sum_gain(self):
        return self.stats['gain'].sum()

    def sum_wins(self):
        return self.stats['wins'].sum()

    def sum_losses(self):
        return self.stats['losses'].sum()

    def avg_winrate(self):
        return self.stats['winrate'].sum() / len(self.stats)

    def longest_trade(self):
        return max(self.stats['longest_trade'])

    def avg_number_of_trades(self):
        return self.stats['number_of_trades'].sum() / len(self.stats)



