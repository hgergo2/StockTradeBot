import mongo_handler as mongo
import pandas as pd
import plotly.express as px


def sum_wins(positions):
    print(len(positions))


def get_profit(positions):
    df = pd.DataFrame(positions)
    if len(df) > 0:
        return float("{:.2f}".format(df['pnl'].sum()))
    return 0



def get_winrate(wins, losses):
    wins = len(wins)
    losses = len(losses)
    if wins + losses > 0:
        return float("{:.2f}".format(((wins / (wins + losses)) * 100)))
    else:
        return 0


def get_pnl_chart(positions):
    if len(positions) <= 0: return -1, -1

    df = pd.DataFrame(positions)
    pnl_data = []

    for n in range(len(positions)):
        current = df.iloc[n]

        if len(pnl_data) == 0:
            pnl_data.append(current['pnl'])
        else:
            pnl_data.append(current['pnl'] + pnl_data[len(pnl_data)-1])
    x_axis = []
    for a in range(0, len(df)):
        x_axis.append(a)
    return x_axis, pnl_data

