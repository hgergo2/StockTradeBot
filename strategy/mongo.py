from pymongo import MongoClient

from strategies_live import Position_live
from strategies_live import ema_strategy_live
import time

cluster = MongoClient('mongodb://localhost:27023/')
charts_db = cluster['Charts']
statistics_db = cluster['Statistics']
positions_db = cluster['Positions']['allPositions']


def add_chart_to_db(symbol, chart, strategy_name, mongo_id):
    if chart is None: return

    if symbol in charts_db.list_collection_names():
        r = charts_db[symbol].find_one({'_id': mongo_id})
        if r is None:
            charts_db[symbol].insert_one({'_id': mongo_id, 'strategy_name': strategy_name, 'chart': chart.to_json()})
        else:
            charts_db[symbol].update_one({'_id': mongo_id}, {
                '$set': {'chart': chart.to_json(), 'strategy_name': strategy_name, 'last_update': time.time()}})
        # print(f'Updated {symbol}')
    else:
        charts_db.create_collection(symbol).insert_one(
            {'_id': mongo_id, 'strategy_name': strategy_name, 'chart': chart.to_json()})


def add_position_to_db(position: Position_live.LivePosition):
    if position is None: return
    positions_db.insert_one({
        '_id': position.mongo_id,
        'symbol': position.symbol,
        'order_type': position.order_type,
        'is_active': position.is_active,
        'entry_price': position.entry_price,
        'entry_date': position.entry_date,
        'target_price': position.target_price,
        'stop_loss': position.stop_loss,
        'sell_price': None,
        'sell_date': None,
        'strategy_name': position.strategy_name
    })


def close_position_db(position: Position_live.LivePosition, sell_candle):
    positions_db.update_one({'_id': position.mongo_id},
                            {'$set': {'is_active': False,
                                      'sell_price': sell_candle['Close'],
                                      'sell_date': sell_candle['DateTime'],
                                      'pnl': calculate_pnl(position, sell_candle)}}
                            )


def update_pnl(position: Position_live.LivePosition, current_candle):

    positions_db.update_one({'_id': position.mongo_id},
                            {'$set': {'pnl': calculate_pnl(position, current_candle)}})


def calculate_pnl(position: Position_live.LivePosition, candle):
    if position.order_type == 'long':
        return float("{:.2f}".format(((candle['Close'] / position.entry_price) - 1) * 100))
    elif position.order_type == 'short':
        return float("{:.2f}".format(((position.entry_price / candle['Close']) - 1) * 100))


def add_statistics_to_db():
    pass


def get_positions(symbol: str):
    symbol.upper()
    pass


def get_latest_position_by_strategy(symbol: str, strategy_name: str):
    symbol.upper()
    strategy_name.lower()
    try:
        return positions_db.find({'symbol': symbol, 'strategy_name': strategy_name}).sort('_id', -1)[0]
    except:
        return None


def get_latest_position_by_id(symbol=None):
    """
    Ha a symbol az None akkor az összes position közül válassza ki a legutóbbit
    """
    if symbol is not None: symbol.upper()

    try:
        if symbol is None:
            return positions_db.find().sort('_id', -1).limit(1)[0]
        else:
            return positions_db.find({'symbol': symbol}).sort('_id', -1).limit(1)[0]
    except:
        return {'_id': -1}
