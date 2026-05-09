import pandas as pd
import pandas_ta as ta
from config import config

def add_indicators(df):
    df = df.copy()
    df['ATR'] = ta.atr(df['High'], df['Low'], df['Close'], length=config.atr_period)
    df['EMA50'] = ta.ema(df['Close'], length=50)
    df['EMA200'] = ta.ema(df['Close'], length=200)
    df['ADX'] = ta.adx(df['High'], df['Low'], df['Close'], length=14)['ADX_14']
    df['RSI'] = ta.rsi(df['Close'], length=7)
    df['VWAP'] = ta.vwap(df['High'], df['Low'], df['Close'], df['Volume'])
    df['STD'] = ta.stdev(df['Close'], length=20)
    return df.dropna()
