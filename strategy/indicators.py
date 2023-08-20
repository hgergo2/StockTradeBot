import math
import pandas as pd

def ema(data: [], length: [int]):
    """
    Exponential Moving Average
    """
    for a in length:
        data[f'ema{a}'] = data['Close'].ewm(span=a, adjust=False).mean()
    return data


def ta(df: [], length=14):
    """
    True Range
    """
    data = df.copy()
    high = data['High']
    low = data['Low']
    close = data['Close']
    data['tr0'] = abs(high - low)
    data['tr1'] = abs(high - close.shift())
    data['tr2'] = abs(low - close.shift())
    tr = data[['tr0', 'tr1', 'tr2']].max(axis=1)
    return tr


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
    return values.ewm(alpha=1 / n, adjust=False).mean()


def value_change(df, column):
    """
    Value change (candle difference)
    """
    data = df.copy()
    close = data[column]
    chng = []
    chng.append(math.nan)
    for a in range(1, len(close)):
        chng.append(close.iloc[a] - close.iloc[a - 1])
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


def adx(df, smoothing=14, length=14):
    """
    Average Directional Index
    """
    data = df.copy()
    adx_results = []
    dx_ = pd.DataFrame(dx(df))
    print(dx_)
    adx_results.append(dx_[:length].sum() / length)
    for i in range(length-1):
        adx_results.append(math.nan)

    for n in range(length, len(df)):
        adx_results.append((adx_results[len(adx_results) - 1] * 13 + dx_.iloc[n]) / length)
    data['adx'] = adx_results
    return data

def dx(df, smoothing=14):
    """
    Directional index
    """
    di = directional_indicator(df, smoothing=smoothing)
    dx_ = []
    for n in range(len(di[0])):
        dx_.append((abs(di[0][n] - di[1][n]) / abs(di[0][n] + di[1][n])) * 100)
    return dx_


def directional_indicator(df, smoothing=14):
    """
    Directional Index Indicator
    """
    df = atr(df)
    directional_indicator_values = [math.nan]
    di_pos_list = [math.nan]
    di_neg_list = [math.nan]
    for n in range(1, len(df)):
        pos = df.iloc[n]['High'] - df.iloc[n - 1]['High']
        neg = df.iloc[n]['Low'] - df.iloc[n - 1]['Low']

        di_pos = ((smoothing + pos) / df.iloc[n]['atr']) * 100
        di_neg = ((smoothing - neg) / df.iloc[n]['atr']) * 100

        di_pos_list.append(di_pos)
        di_neg_list.append(di_neg)

    # if pos > neg:
    #    di_pos = ((smoothing + pos) / df.iloc[n]['atr']) * 100
    #    directional_indicator_values.append(di_pos)
    # elif neg > pos:
    #    di_neg = ((smoothing - neg) / df.iloc[n]['atr']) * 100
    #    directional_indicator_values.append(di_neg)
    return di_pos_list, di_neg_list
