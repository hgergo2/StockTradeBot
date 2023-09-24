from pymongo import MongoClient
import pandas as pd
import Position_live
import time
import configparser

config = configparser.ConfigParser()
config.read('mongo_config.ini')

def __get_positions_db():
    if 'Positions' in cluster.list_database_names():
        if 'allPositions' not in cluster['Positions'].list_collection_names():
            print('Creating allPositions collection')
            cluster['Positions'].create_collection('allPositions')
            return cluster['Positions']['allPositions']
        else:
            print('Found allPositions db')
            return cluster['Positions']['allPositions']
    else:
        print('creating Positions db')
        mydb = cluster['Positions']['allPositions']
        mydb.insert_one({'_id': 0})
        mydb.delete_one({'_id': 0})
        return mydb


cluster = MongoClient(str(config['MONGO']['mongo_url']))
charts_db = cluster['Charts']
statistics_db = cluster['Statistics']
positions_db = __get_positions_db()

#priceDataCluster = MongoClient('mongodb://localhost:27017/')
historical_db = cluster['priceData']['historical']


def get_price_data(symbol: str, timeframe: str):
    symbol.upper()
    timeframe.lower()

    data = historical_db.find_one({'symbol': symbol, 'timeframe': timeframe})
    df = pd.DataFrame({'Open': data['Open'],
                       'High': data['High'],
                       'Low': data['Low'],
                       'Close': data['Close'],
                       'Volume': data['Volume'],
                       'DateTime': data['DateTime']})
    return df


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
