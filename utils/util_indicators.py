# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

__author__ = 'Ishafizan'
__date__: "15 Feb 2025"

import talib
from utils import util_gen, util_signals


def calculate_indicators(df):
    """
    Compute essential technical indicators for signal detection.

    Indicators included:
    - Exponential Moving Averages (EMA) to identify trend direction.
    - Relative Strength Index (RSI) to measure momentum and overbought/oversold conditions.
    - Support & Resistance levels based on the 20-period rolling min/max.
    - 20-period Volume Moving Average (Volume_MA) to detect volume surges.

    Parameters:
    df (DataFrame): Historical price data containing OHLCV (Open, High, Low, Close, Volume).

    Returns:
    DataFrame: The input dataframe with additional indicator columns.
    """
    # Compute Exponential Moving Averages (EMAs) for trend analysis
    df["EMA7"] = calculate_ema(df, 7)  # Short-term EMA for quick momentum shifts
    df["EMA21"] = calculate_ema(df, 21)  # Confirms short-term trend
    df["EMA50"] = calculate_ema(df, 50)  # Mid-term trend confirmation
    df["EMA100"] = calculate_ema(df, 100)  # Long-term trend identification
    df["EMA200"] = calculate_ema(df, 200)  # Major trend direction (Golden/Death Cross)

    # Compute RSI (Relative Strength Index) to assess overbought/oversold conditions
    df["RSI"] = calculate_rsi(df["close"])

    # Identify support (local lows) and resistance (local highs) using a rolling 20-period window
    df["Support"] = df["close"].rolling(20).min()
    df["Resistance"] = df["close"].rolling(20).max()

    # Calculate 20-period moving average of volume to detect unusual spikes in trading activity
    df["Volume_MA"] = df["volume"].rolling(window=20).mean()

    # Compute ADX (Average Directional Index) to measure trend strength
    # ADX values above 25 indicate a strong trend, while values below 20 suggest a weak or ranging market.
    df["ADX"] = calculate_adx(df)

    return df


def calculate_ema(df, span):
    """
    Calculate EMAs
    """
    return df["close"].ewm(span=span, adjust=False).mean()


def calculate_rsi(series, period=14):
    """
    Calculate the Relative Strength Index (RSI).

    RSI is a momentum oscillator that measures the speed and change of price movements.
    It ranges from 0 to 100 and is used to identify overbought or oversold conditions:

    - RSI > 70: Overbought (potential sell signal)
    - RSI < 30: Oversold (potential buy signal)

    Parameters:
    - series (pd.Series): A Pandas Series of closing prices.
    - period (int): The lookback period for RSI calculation (default: 14).

    Returns:
    - pd.Series: RSI values.
    """

    # Calculate price changes (difference between consecutive prices)
    delta = series.diff()

    # Identify gains (positive changes) and losses (negative changes)
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

    # Compute the Relative Strength (RS): average gain / average loss
    rs = gain / loss

    # Compute RSI using the standard formula
    rsi = 100 - (100 / (1 + rs))

    return rsi


def calculate_adx(df, period=14):
    """
    Calculate the Average Directional Index (ADX) to measure trend strength.

    ADX helps traders determine if a trend is strong or weak:
    - ADX > 25: Strong trend (uptrend or downtrend)
    - ADX < 25: Weak or ranging market (sideways movement)

    Parameters:
    - df (pd.DataFrame): A Pandas DataFrame containing 'high', 'low', and 'close' prices.
    - period (int): The lookback period for ADX calculation (default: 14).

    Returns:
    - pd.Series: ADX values indicating trend strength.
    """

    # Calculate True Range (TR) as the absolute difference between high and low
    df["high-low"] = df["high"] - df["low"]

    # Calculate Directional Movement (DM)
    df["+DM"] = df["high"].diff().where(df["high"].diff() > df["low"].diff(), 0)
    df["-DM"] = -df["low"].diff().where(df["low"].diff() > df["high"].diff(), 0)

    # Calculate the Directional Indicators (DI) using a rolling average
    df["+DI"] = (df["+DM"].rolling(window=period).mean() / df["high-low"].rolling(window=period).mean()) * 100
    df["-DI"] = (df["-DM"].rolling(window=period).mean() / df["high-low"].rolling(window=period).mean()) * 100

    # Calculate the Directional Index (DX)
    df["DX"] = abs(df["+DI"] - df["-DI"]) / (df["+DI"] + df["-DI"]) * 100

    # Calculate the Average Directional Index (ADX) using a rolling mean of DX
    df["ADX"] = df["DX"].rolling(window=period).mean()

    return df["ADX"]


def detect_support_resistance(df, period=20):
    """
    Detects key Support and Resistance levels using a rolling window.

    Support: The lowest price over the last 'period' candles.
    Resistance: The highest price over the last 'period' candles.

    These levels help identify potential reversal or breakout zones.
    """
    df["Support"] = df["close"].rolling(period).min()  # Rolling minimum price over 'period' candles (Support level)
    df["Resistance"] = df["close"].rolling(
        period).max()  # Rolling maximum price over 'period' candles (Resistance level)
    return df


def calculate_atr(df, period=14):
    """
    Calculate the Average True Range (ATR) to measure market volatility.

    ATR helps traders:
    - Identify periods of high or low volatility.
    - Filter out weak breakouts by ensuring price moves are significant.
    - Set dynamic stop-loss and take-profit levels based on recent price swings.

    The ATR formula:
    1. True Range (TR) is the maximum of:
       - Current High - Current Low
       - Absolute difference between Current High and Previous Close
       - Absolute difference between Current Low and Previous Close
    2. ATR is the smoothed moving average of TR over the given 'period'.

    Args:
    df (pd.DataFrame): DataFrame containing 'high', 'low', and 'close' prices.
    period (int): The number of periods used to calculate ATR (default: 14).

    Returns:
    pd.DataFrame: Updated DataFrame with a new column 'ATR' representing market volatility.
    """
    df["ATR"] = talib.ATR(df["high"], df["low"], df["close"], timeperiod=period)
    return df





