import mongo_handler as mongo
import pandas as pd

def sum_wins(positions):
    print(len(positions))


def get_profit(positions):
    df = pd.DataFrame(positions)
    return float("{:.2f}".format(df['pnl'].sum()))


def get_winrate(wins, losses):
    wins = len(wins)
    losses = len(losses)
    if wins + losses > 0:
        return float("{:.2f}".format(((wins / (wins + losses)) * 100)))
    else:
        return -1



