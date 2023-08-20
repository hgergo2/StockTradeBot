import random
import string

import pandas as pd
import yfinance as yf

#15 min limit: 60d
#60min limit: 730d

def get_data(ticker_: str, timeFrame: str, period: str):
    ticker_.upper()
    timeFrame.lower()
    period.lower()

    try:
        ticker = yf.Ticker(ticker_)
        bars = pd.DataFrame(ticker.history(period=period, interval=timeFrame)).drop(columns=['Dividends', 'Stock Splits'])
        bars['DateTime'] = bars.index
        bars.index = list(range(0,len(bars)))
        datetimes = []
        for i in range(len(bars)):
            new_datetime = str(bars.iloc[i]['DateTime'])[:19]
            datetimes.append(new_datetime)
            #19db
        bars['DateTime'] = datetimes
    except:
        return -1
    return bars

def get_data_multiple_symbols(symbols: [str], timeframe: str, period: str):
    """
    Minimum 3 db symbolnak kell benne lennie
    """
    if len(symbols) < 3: return
    for a in symbols: a.upper()
    timeframe.lower()
    period.lower()

    try:
        ticker = yf.Tickers(symbols)
        bars = pd.DataFrame(ticker.history(period=period, interval=timeframe, progress=False)).drop(columns=['Dividends', 'Stock Splits', 'Capital Gains'])
        bars['DateTime'] = bars.index
        bars.index = list(range(0, len(bars)))
        return bars
    except:
        return -1


