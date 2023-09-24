import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import pandas as pd
import yfinance as yf

__valid_timeframes = ['1m', '5m', '15m', '30m', '60m', '1d', 'max']


def get_data(symbols: [str], timeframe: str, period: str):
    """
    A symbolsnak legalább 3 elem hosszúnak kell lennie
    """

    if len(symbols) < 3:
        raise Exception('A symbols listának legalább 3 elem hosszúnak kell lennie')

    if timeframe.lower() not in __valid_timeframes:
        raise Exception('A timeframe nem megfelelő')

    for symbol in symbols: symbol.upper()

    try:
        ticker = yf.Tickers(symbols)
        bars = pd.DataFrame(ticker.history(period=period, interval=timeframe, progress=False)).drop(
            columns=['Dividends', 'Stock Splits', 'Capital Gains'])
        bars['DateTime'] = bars.index
        bars.index = list(range(0, len(bars)))
        return bars
    except:
        return -1



