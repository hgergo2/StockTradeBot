import math

import pandas as pd

def ema(data: [], length: [int]):
    """
    Exponential Moving Average
    """
    for a in length:
        data[f'ema200'] = data['Close'].ewm(span=a, adjust=False).mean()
    return data


def ta(data: [], length):
    """
    True Range
    """

    for i in range(length, len(data)):
        candle = data.iloc[i]
        max(candle['High'] - candle['Low'], data.iloc[i])


def atr(df, n=14):
    """
    Average True Range
    """
    data = df.copy()
    high = data['High']
    low = data['Low']
    close = data['Close']
    data['tr0'] = abs(high - low)
    data['tr1'] = abs(high - close.shift())
    data['tr2'] = abs(low - close.shift())
    tr = data[['tr0', 'tr1', 'tr2']].max(axis=1)
    atr = wwma(tr, n)
    data['atr'] = atr
    return data.drop(columns=['tr0', 'tr1', 'tr2'])

def wwma(values, n):
    """
     J. Welles Wilder's EMA
    """
    return values.ewm(alpha=1/n, adjust=False).mean()

def value_change(df, column):
    """
    Value change (candle difference)
    """
    data = df.copy()
    close = data[column]
    chng = []
    chng.append(math.nan)
    for a in range(1, len(close)):
        chng.append(close.iloc[a] - close.iloc[a-1])
    data['change'] = chng
    return data

def avg_value_change(df, column, length=14):
    """
    Average value change (average candle difference)
    """
    df = value_change(df, column)
    data = df.copy()
    data['avg_value_change'] = wwma(df['change'], length)
    return data


