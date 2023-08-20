import pymongo
from pymongo import MongoClient
import statistics

cluster = MongoClient('mongodb://localhost:27023/')
charts_db = cluster['Charts']
statistics_db = cluster['Statistics']
positions_db = cluster['Positions']['allPositions']

symbols = ['NVDA', 'TSLA', 'TQQQ', 'AMD', 'INTC', 'AMC', 'SHOP', 'ENVX', 'GOOG']


def get_chart(symbol, strategy_name):
    try:
        result = charts_db[symbol].find_one({'strategy_name': strategy_name})['chart']
    except Exception:
        return -1
    return result


def get_positions(symbol=None, strategy=None, active=None):
    query = {}

    if symbol is not None:
        query['symbol'] = symbol.upper()
    if strategy is not None:
        query['strategy_name'] = strategy.lower()
    if active is not None:
        res = True
        if str(active).lower() == 'false':
            res = False
        query['is_active'] = res

    return list(positions_db.find(query))


def get_statistics():
    wins = list(positions_db.find({'is_active': False,
                                   'pnl': {'$gte': 0}}))
    losses = list(positions_db.find({'is_active': False,
                                     'pnl': {'$lt': 0}}))
    all_inactive_pos = list(positions_db.find({'is_active': False}))
    all_active_pos = list(positions_db.find({'is_active': True}))

    end = {
        'wins': len(wins),
        'losses': len(losses),
        'pnl': statistics.get_profit(all_inactive_pos),
        'winrate': statistics.get_winrate(wins, losses),
        'number_of_active': len(all_active_pos),
        'active_pnl': statistics.get_profit(all_active_pos)
    }

    return end


def calc_all_pnl():
    all_positions = list(positions_db.find({'is_active': False}))

    for pos in all_positions:
        # Ha long position akkor ((sell_price / entry_price) - 1) * 100
        # Ha short position akkor ((entry_price / sell_price) - 1) * 100
        pnl = 0

        if pos['order_type'] == 'long':
            pnl = ((pos['sell_price'] / pos['entry_price']) - 1) * 100
        elif pos['order_type'] == 'short':
            pnl = ((pos['entry_price'] / pos['sell_price']) - 1) * 100

        positions_db.update_one({'_id': pos['_id']},
                                {'$set': {'pnl': pnl}}
                                )
