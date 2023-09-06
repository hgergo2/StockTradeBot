import datetime

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


def get_statistics(start=None, end=None, strategies=None):
    wins_query = {
        'is_active': False,
        'pnl': {'$gte': 0}
    }
    loss_query = {
        'is_active': False,
        'pnl': {'$lt': 0}
    }
    all_active_query = {
        'is_active': True
    }
    all_inactive_query = {
        'is_active': False
    }
    date_query = {}
    if start is not None:
        start = str(start).split('-')
        date_query['$gte'] = datetime.datetime(int(start[0]),
                                               int(start[1]),
                                               int(start[2]),0,0)

    if end is not None:
        end = str(end).split('-')

        date_query['$lte'] = datetime.datetime(int(end[0]),
                                               int(end[1]),
                                               int(end[2]), 23, 59)

    if strategies is not None:
        result = str(strategies).split(',')
        wins_query['strategy_name'] = {'$in': result}
        loss_query['strategy_name'] = {'$in': result}
        all_inactive_query['strategy_name'] = {'$in': result}
        all_active_query['strategy_name'] = {'$in': result}

    wins_query['sell_date'] = date_query
    loss_query['sell_date'] = date_query
    all_active_query['entry_date'] = date_query
    all_inactive_query['entry_date'] = date_query

    wins = list(positions_db.find(wins_query))
    losses = list(positions_db.find(loss_query))
    all_inactive_pos = list(positions_db.find(all_inactive_query).sort('entry_date', 1))
    all_active_pos = list(positions_db.find(all_active_query))
    chart_data = statistics.get_pnl_chart(all_inactive_pos)

    active_pnl = statistics.get_profit(all_active_pos)
    pnl = statistics.get_profit(all_inactive_pos)

    stats = {
        'wins': len(wins),
        'losses': len(losses),
        'pnl': pnl,
        'winrate': statistics.get_winrate(wins, losses),
        'number_of_active': len(all_active_pos),
        'active_pnl': active_pnl,
        'stats_chart_x': chart_data[0],
        'stats_chart_y': chart_data[1],
        'overall_pnl': float("{:.2f}".format(active_pnl + pnl))
    }
    return stats


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
