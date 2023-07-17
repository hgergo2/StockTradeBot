import pandas as pd
import yfinance as yf

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