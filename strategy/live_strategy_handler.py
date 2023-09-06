import mongo
from strategies_live import ema_strategy_live
from strategies_live import random_live
from strategies_live import support_and_resistance_live
from strategies_live import macd_bollinger_live

class strategy_handler:
    def __init__(self):
        self.strategies = []

    def run_strategies(self, new_data, new_data_30m, new_data_60m):

        for strategy in self.strategies:
            result = None
            if strategy.strategy_name == '200ema_strategy':
                result = strategy.run_strategy(new_data, new_data_30m, new_data_60m)
            elif strategy.strategy_name == 'random_strategy':
                result = strategy.run_strategy(new_data)
            elif strategy.strategy_name == 'support_and_resistance':
                result = strategy.run_strategy(new_data, max_stop_loss=0.02)
            elif strategy.strategy_name == 'macd_bollinger':
                result = strategy.run_strategy(new_data)
            mongo.add_chart_to_db(strategy.symbol, result[1], strategy.strategy_name, result[2])

    def add_strategy(self, symbols: [str], strategy_name: str, start_data, start_data_30m, start_data_60m):
        for symbol in symbols:
            if strategy_name == '200ema':
                self.strategies.append(ema_strategy_live.strategy(symbol, start_data,
                                                                       start_data_30m, start_data_60m))
            elif strategy_name == 'random':
                self.strategies.append(random_live.strategy(symbol, start_data))
            elif strategy_name == 'support_and_resistance':
                self.strategies.append(support_and_resistance_live.strategy(symbol, start_data))
            elif strategy_name == 'macd_bollinger':
                self.strategies.append(macd_bollinger_live.strategy(symbol, start_data))
