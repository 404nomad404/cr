# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

__author__ = 'Ishafizan'
__date__ = "15 Feb 2025"

import talib
import settings
from utils.util_gen import fetch_cme_open_interest, fetch_binance_open_interest
from utils.util_log import logger

# Initialize logger for tracking indicator calculations
log = logger()


def calculate_indicators(df):
    """
    Computes a suite of technical indicators for trading signal generation.

    Indicators:
    - EMAs: Based on configurable periods for trend detection.
    - RSI: Momentum oscillator with dynamic period.
    - ADX: Trend strength indicator (14-period default).
    - ATR: Volatility measure (14-period default).
    - Volume MA: 20-period moving average for volume trends.
    - Support/Resistance: Rolling min/max over 20 periods.
    - WVIX: Williams VIX Fix for market bottom detection.
    - Stochastic: Oscillator for overbought/oversold conditions.
    - Institutional: Open interest data if available.

    Args:
        df (pd.DataFrame): Historical OHLCV data.

    Returns:
        pd.DataFrame: Dataframe with added indicator columns.
    """
    config = settings.TREND_CONFIG[settings.MIN_TREND_STRENGTH]

    # Calculate EMAs for trend analysis
    for period in config["EMA_PERIODS"]:
        df[f"EMA{period}"] = df["close"].ewm(span=period, adjust=False).mean()

    # Momentum indicator: RSI
    df["RSI"] = calculate_rsi(df["close"], period=config['RSI_PERIOD'])

    # Trend strength: ADX
    df["ADX"] = calculate_adx(df, period=14)

    # Volatility: ATR
    df = calculate_atr(df, period=14)

    # Volume trend: 20-period MA
    df['Volume_MA'] = df['volume'].rolling(window=20).mean()

    # Support and resistance levels
    df["Support"] = df["close"].rolling(20).min()
    df["Resistance"] = df["close"].rolling(20).max()

    # Breakout threshold for detection
    df['Breakout_Threshold'] = df['close'].rolling(window=20).max() * (1 + config['BREAKOUT_PERCENTAGE'])

    # Additional indicators
    df = williams_vix_fix(df)
    df = calculate_stochastic(df)
    df = calculate_institutional_indicators(df)

    return df


def calculate_ema(df, span):
    """
    Calculates Exponential Moving Average for a given period.

    Args:
        df (pd.DataFrame): Dataframe with 'close' prices.
        span (int): EMA period.

    Returns:
        pd.Series: EMA values.
    """
    return df["close"].ewm(span=span, adjust=False).mean()


def calculate_rsi(series, period=14):
    """
    Computes Relative Strength Index (RSI) to gauge momentum.

    - RSI > 70: Overbought (potential sell).
    - RSI < 30: Oversold (potential buy).

    Args:
        series (pd.Series): Closing prices.
        period (int): Lookback period (default 14, overridden by config).

    Returns:
        pd.Series: RSI values.
    """
    config = settings.TREND_CONFIG[settings.MIN_TREND_STRENGTH]
    period = config["RSI_PERIOD"]

    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


def calculate_adx(df, period=14):
    """
    Calculates Average Directional Index (ADX) for trend strength.

    - ADX > 25: Strong trend.
    - ADX < 25: Weak or ranging market.

    Args:
        df (pd.DataFrame): Data with 'high', 'low', 'close'.
        period (int): Lookback period (default 14).

    Returns:
        pd.Series: ADX values.
    """
    df["high-low"] = df["high"] - df["low"]
    df["+DM"] = df["high"].diff().where(df["high"].diff() > df["low"].diff(), 0)
    df["-DM"] = -df["low"].diff().where(df["low"].diff() > df["high"].diff(), 0)
    df["+DI"] = (df["+DM"].rolling(window=period).mean() / df["high-low"].rolling(window=period).mean()) * 100
    df["-DI"] = (df["-DM"].rolling(window=period).mean() / df["high-low"].rolling(window=period).mean()) * 100
    df["DX"] = abs(df["+DI"] - df["-DI"]) / (df["+DI"] + df["-DI"]) * 100
    df["ADX"] = df["DX"].rolling(window=period).mean()

    return df["ADX"]


def detect_support_resistance(df, period=20):
    """
    Identifies support and resistance levels using rolling min/max.

    - Support: Lowest price over period.
    - Resistance: Highest price over period.

    Args:
        df (pd.DataFrame): OHLCV data.
        period (int): Rolling window (default 20).

    Returns:
        pd.DataFrame: Dataframe with 'Support' and 'Resistance' columns.
    """
    df["Support"] = df["close"].rolling(period).min()
    df["Resistance"] = df["close"].rolling(period).max()
    return df


def calculate_atr(df, period=14):
    """
    Calculates Average True Range (ATR) for volatility assessment.

    ATR measures price volatility to filter breakouts and set trade levels.

    Args:
        df (pd.DataFrame): Data with 'high', 'low', 'close'.
        period (int): Lookback period (default 14).

    Returns:
        pd.DataFrame: Dataframe with 'ATR' column.
    """
    df["ATR"] = talib.ATR(df["high"], df["low"], df["close"], timeperiod=period)
    return df


def calculate_trend_score(df):
    """
    Computes a trend score (0-100) based on multiple factors.

    Factors:
    - EMA alignment: 30 points for strong trend.
    - ADX: Up to 30 points for strength.
    - RSI: Up to 15 points for momentum.
    - Breakout: 15 points if present.
    - Volume: 10 points if above average.

    Args:
        df (pd.DataFrame): Data with indicators.

    Returns:
        int: Trend score capped at 100.
    """
    latest = df.iloc[-1]
    score = 0

    if latest["EMA50"] > latest["EMA100"] > latest["EMA200"]:
        score += 30
    elif latest["EMA50"] < latest["EMA100"] < latest["EMA200"]:
        score += 30

    if latest["ADX"] > 25:
        score += 30
    elif latest["ADX"] > 20:
        score += 20

    if 40 < latest["RSI"] < 60:
        score += 10
    elif latest["RSI"] >= 60 or latest["RSI"] <= 40:
        score += 15

    if "breakout" in latest and latest["breakout"]:
        score += 15

    if "volume" in latest and latest["volume"] > df["volume"].rolling(20).mean().iloc[-1]:
        score += 10

    return min(score, 100)


def calculate_macd(df, short_window=12, long_window=26, signal_window=9):
    """
    Computes MACD indicator for trend and momentum analysis.

    - MACD Line: Short EMA - Long EMA.
    - Signal Line: EMA of MACD Line.
    - Histogram: MACD Line - Signal Line.

    Args:
        df (pd.DataFrame): Data with 'close' prices.
        short_window (int): Short EMA period (default 12).
        long_window (int): Long EMA period (default 26).
        signal_window (int): Signal EMA period (default 9).

    Returns:
        pd.DataFrame: Dataframe with MACD columns.
    """
    df['MACD_Line'] = df['close'].ewm(span=short_window, adjust=False).mean() - df['close'].ewm(span=long_window, adjust=False).mean()
    df['Signal_Line'] = df['MACD_Line'].ewm(span=signal_window, adjust=False).mean()
    df['MACD_Histogram'] = df['MACD_Line'] - df['Signal_Line']
    return df


def check_breakout(price, level, direction, latest, atr_threshold, volume_multiplier):
    """
    Confirms a breakout based on price movement, ATR, and volume.

    Args:
        price (float): Current price.
        level (float): S/R level.
        direction (str): "BUY" or "SELL".
        latest (pd.Series): Latest data.
        atr_threshold (float): Minimum price move.
        volume_multiplier (float): Volume threshold.

    Returns:
        bool: True if breakout confirmed.
    """
    is_breakout = price > level if direction == "BUY" else price < level
    prev_price_below_resistance = latest["Prev_Close"] <= level if direction == "BUY" else latest["Prev_Close"] >= level

    if is_breakout and prev_price_below_resistance:
        volume_confirmed = latest["volume"] > (latest["Avg_Volume"] * volume_multiplier)
        price_move = abs(latest["close"] - level) if direction == "BUY" else abs(level - latest["close"])
        if volume_confirmed and price_move > atr_threshold:
            return True
    return False


def evaluate_double_down(all_signals_status, trend_status, latest):
    """
    Assesses conditions for doubling down on a BUY signal.

    Requires strong trend (ADX) and high volume.

    Args:
        all_signals_status (str): Overall signal status.
        trend_status (str): Current trend.
        latest (pd.Series): Latest data.

    Returns:
        bool: True if double-down recommended.
    """
    config = settings.TREND_CONFIG[settings.MIN_TREND_STRENGTH]
    adx_threshold = config["ADX_THRESHOLD"]
    volume_multiplier = config["VOLUME_MULTIPLIER"]

    valid_trend_statuses = ["Strong Uptrend", "Moderate Uptrend"]
    if settings.MIN_TREND_STRENGTH == "Weak":
        valid_trend_statuses.append("Weak Uptrend")

    if all_signals_status == "BUY" and trend_status in valid_trend_statuses:
        if latest["ADX"] > adx_threshold and latest["volume"] > latest["Volume_MA"] * volume_multiplier:
            return True
    return False


def williams_vix_fix(df, period=22, bb_period=20, mult=2):
    """
    Calculates Williams VIX Fix to detect market bottoms.

    - WVIX: Measures panic selling.
    - Bollinger Bands: Contextualize WVIX extremes.

    Args:
        df (pd.DataFrame): OHLCV data.
        period (int): WVIX lookback (default 22).
        bb_period (int): Bollinger Band period (default 20).
        mult (float): Bollinger Band multiplier (default 2).

    Returns:
        pd.DataFrame: Dataframe with WVIX and BB columns.
    """
    df['WVIF'] = ((df['high'].rolling(window=period).max() - df['close']) / df['high'].rolling(window=period).max()) * 100
    df['WVIF_SMA'] = df['WVIF'].rolling(window=bb_period).mean()
    df['WVIF_STD'] = df['WVIF'].rolling(window=bb_period).std()
    df['WVIF_BB_UPPER'] = df['WVIF_SMA'] + (df['WVIF_STD'] * mult)
    df['WVIF_BB_LOWER'] = df['WVIF_SMA'] - (df['WVIF_STD'] * mult)
    return df


def calculate_stochastic(df):
    """
    Computes Stochastic Oscillator for overbought/oversold detection.

    - FastK/FastD < 20: Oversold.
    - FastK/FastD > 80: Overbought.

    Args:
        df (pd.DataFrame): OHLCV data.

    Returns:
        pd.DataFrame: Dataframe with 'fastk' and 'fastd' columns.
    """
    df['fastk'], df['fastd'] = talib.STOCH(
        df['high'], df['low'], df['close'],
        fastk_period=14, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0
    )
    return df


def calculate_institutional_indicators(df):
    """
    Adds institutional indicators like open interest from CME or Binance.

    Falls back to Binance OI if CME data fails.

    Args:
        df (pd.DataFrame): OHLCV data.

    Returns:
        pd.DataFrame: Dataframe with 'CME_Open_Interest' column.
    """
    try:
        oi = fetch_cme_open_interest()
        if oi is None:
            log.warning("Falling back to Binance OI due to CME fetch failure")
            oi = fetch_binance_open_interest()
        df["CME_Open_Interest"] = oi
    except Exception as e:
        log.warning(f"Failed to fetch OI: {e}")
    return df
