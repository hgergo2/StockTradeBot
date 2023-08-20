from strategies_live import LiveChartHandler
from strategies_live import Position_live
import mongo


class OrderHandlerLive:
    def __init__(self, symbol: str, timeframe: str, data, strategy_name: str):
        self.symbol = symbol
        self.position = None
        self.timeframe = timeframe
        self.data = data
        self.strategy_name = strategy_name
        self.chart = LiveChartHandler.LiveChart(symbol=symbol, timeframe=timeframe, data=self.data)
        print(self.symbol)
        latest_position = mongo.get_latest_position_by_strategy(self.symbol, self.strategy_name)
        if latest_position is not None and latest_position['is_active']:
            self.position = Position_live.LivePosition(symbol=latest_position['symbol'],
                                                       order_type=latest_position['order_type'],
                                                       is_active=latest_position['is_active'],
                                                       entry_price=latest_position['entry_price'],
                                                       entry_date=latest_position['entry_date'],
                                                       target_price=latest_position['target_price'],
                                                       stop_loss=latest_position['stop_loss'],
                                                       mongo_id=latest_position['_id'],
                                                       strategy_name=latest_position['strategy_name'])
            self.chart.position = self.position
            print(f'Loaded position with id: {self.position.mongo_id} on {self.symbol}')
            print(latest_position)
        else:
            print(latest_position)
            print(f'Found no active positions | strategy: {self.strategy_name}')

    def open_position(self, order_type: str, buy_candle, target_price=None, stop_loss=None, info=False):
        if self.position is not None: return
        mong_id = mongo.get_latest_position_by_id()['_id']+1
        #if self.symbol in mongo.positions_db.list_collection_names():
        #    r = mongo.get_latest_position_by_id()
        #    if r is not None: mong_id = r['_id']+1

        pos = Position_live.LivePosition(symbol=self.symbol,
                                         order_type=order_type,
                                         is_active=True,
                                         entry_price=buy_candle['Close'],
                                         entry_date=buy_candle['DateTime'],
                                         target_price=target_price,
                                         stop_loss=stop_loss,
                                         mongo_id=mong_id,
                                         strategy_name=self.strategy_name)
        self.chart.position = pos
        self.position = pos
        mongo.add_position_to_db(pos)
        if info:
            print(f'Opened {order_type} on {self.symbol}, strategy:{self.strategy_name}')

    def close_position(self, sell_candle):
        if self.position is None:
            print(f'cant close, position is None on {self.symbol}')
            return
        print(f'Closing position on {self.symbol} strategy: {self.strategy_name}')
        mongo.close_position_db(self.position, sell_candle)
        self.position = None
        self.chart.position = None

    def check_position(self, current_candle):
        if self.position is None:
            #print('Position was None')
            return
        if self.position.target_price is None or self.position.stop_loss is None:
            #print('Traget price or stop loss was none')
            return

        if self.position.order_type == 'long':
            if current_candle['Close'] >= self.position.target_price:
                # Long Win
                #print('long win')
                self.close_position(current_candle)
            elif current_candle['Close'] <= self.position.stop_loss:
                # Long lose
                #print('long lose')
                self.close_position(current_candle)
        elif self.position.order_type == 'short':
            if current_candle['Close'] >= self.position.stop_loss:
                # Short lose
                #print('Short lose')
                self.close_position(current_candle)
            elif current_candle['Close'] <= self.position.target_price:
                # Short win
                #print('Short win')
                self.close_position(current_candle)
