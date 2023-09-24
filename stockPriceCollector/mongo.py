import time

from pymongo import MongoClient

cluster = MongoClient('mongodb://localhost:27023/')


def __get_historical_db():
    if 'priceData' in cluster.list_database_names():
        if 'historical' not in cluster['priceData'].list_collection_names():
            print('Creating historical collection')
            cluster['priceData'].create_collection('historical')
            return cluster['priceData']['historical']
        else:
            print('Found historical collection')
            return cluster['priceData']['historical']
    else:
        print('Creating historical DB')
        mydb = cluster['priceData']['historical']
        mydb.insert_one({'_id': 0})
        mydb.delete_one({'_id': 0})
        return mydb


def __get_latest_db():
    if 'priceData' in cluster.list_database_names():
        if 'latest' not in cluster['priceData'].list_collection_names():
            print('creating latest Collection')
            cluster['priceData'].create_collection('latest')
            return cluster['priceData']['latest']
        else:
            print('Found latest collection')
            return cluster['priceData']['latest']
    else:
        print('Creating latest DB')
        mydb = cluster['priceData']['latest']
        mydb.insert_one({'_id': 0})
        mydb.delete_one({'_id': 0})
        return mydb


historical_db = __get_historical_db()
latest_db = __get_latest_db()


def add_data_with_history(symbol: str, open: [], high: [], low: [], close: [], volume: [], candletime: [],
                          timeframe: str, period: str):
    # Egy adott timeframe adott periodnyi adatait adja hozzá és mindig arra cseréli ki az egészet
    symbol.upper()
    timeframe.lower()
    period.lower()
    if historical_db.find_one({'symbol': symbol, 'timeframe': timeframe}) is None:
        historical_db.insert_one({'symbol': symbol,
                                  'timeframe': timeframe,
                                  'period': period,
                                  'last_update': time.time(),
                                  'Open': open,
                                  'High': high,
                                  'Low': low,
                                  'Close': close,
                                  'Volume': volume,
                                  'DateTime': candletime})
    else:
        historical_db.update_one({'symbol': symbol, 'timeframe': timeframe}, {'$set': {'period': period,
                                                                                       'last_update': time.time(),
                                                                                       'Open': open,
                                                                                       'High': high,
                                                                                       'Low': low,
                                                                                       'Close': close,
                                                                                       'Volume': volume,
                                                                                       'DateTime': candletime}})


def add_latest_data():
    # Csak a legújabb close price-t adja hozzá
    pass
