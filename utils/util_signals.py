# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

__author__ = 'Ishafizan'
__date__: "15 Feb 2025"

import pandas as pd
import json
from utils import util_gen, util_indicators


def detect_ema_crossovers(latest, previous):
    """
    Identify EMA crossover signals with ADX and volume confirmation.

    This function detects key EMA crossovers and validates them using:
    - ADX > 25 for trend strength confirmation.
    - Volume spike (above 20-period moving average) to confirm breakout strength.

    Parameters:
    latest (dict): The most recent price data, including EMAs, ADX, and volume.
    previous (dict): The previous period's price data for comparison.

    Returns:
    tuple:
        - signals (list): Messages indicating detected EMA crossovers.
        - status (str): Overall trading action determined (BUY, SELL, or HOLD).
        - ema_cross_flag (bool): Flag indicating if any crossover occurred.
    """

    signals = []  # Stores detected crossover messages
    ema_cross_flag = False  # Track if any crossover happened
    status = "HOLD"  # Default action if no crossover occurs

    # Extract ADX value and volume conditions
    adx_value = latest.get("ADX", 0)
    high_volume = latest["volume"] > latest["Volume_MA"]

    # Define EMA crossover conditions: (short EMA, long EMA, messages, signal type)
    crossover_conditions = [
        ("EMA21", "EMA50", "📈 *EMA21 crossed above EMA50*", "📉 *EMA21 crossed below EMA50*", "BUY", "SELL"),
        ("EMA100", "EMA200", "✅ *EMA100 crossed above EMA200 (Golden Cross)*",
         "❌ *EMA100 crossed below EMA200 (Death Cross)*", "BUY", "SELL"),
        ("EMA50", "EMA100", "✅ *EMA50 crossed above EMA100*", "❌ *EMA50 crossed below EMA100*", "BUY", "SELL"),
        ("EMA7", "EMA21", "✅ *EMA7 crossed above EMA21 (Short-term Buy)*",
         "❌ *EMA7 crossed below EMA21 (Short-term Sell)*", "BUY", "SELL")
    ]

    # Check for each EMA crossover condition
    for short_ema, long_ema, bullish_msg, bearish_msg, buy_status, sell_status in crossover_conditions:
        bullish_crossover = latest[short_ema] > latest[long_ema] and previous[short_ema] <= previous[long_ema]
        bearish_crossover = latest[short_ema] < latest[long_ema] and previous[short_ema] >= previous[long_ema]

        # Use the index as the date
        latest_date = latest.name if hasattr(latest, "name") else "UNKNOWN_DATE"

        if bullish_crossover:
            msg = bullish_msg
            if adx_value > 25:
                msg += " 🔥 (Confirmed by ADX > 25)"
            if high_volume:
                msg += " 🚀 (Confirmed by High Volume)"
            msg += f"\n🚀 BUY SIGNAL: {bullish_msg} at price {latest['close']} on {latest_date}"
            # print(f"\n🚀 BUY SIGNAL: {bullish_msg} at price {latest['close']} on {latest_date}")
            signals.append(msg)
            ema_cross_flag = True
            status = buy_status  # Update status to BUY

        if bearish_crossover:
            msg = bearish_msg
            if adx_value > 25:
                msg += " 🔴 Confirmed by ADX > 25"
            if high_volume:
                msg += " 🔴 Confirmed by High Volume"
            msg += f"\n🚀 SELL SIGNAL: {bearish_msg} at price {latest['close']} on {latest_date}"
            # print(f"🔻 SELL SIGNAL: {bearish_msg} at price {latest['close']} on {latest_date}")
            signals.append(msg)
            ema_cross_flag = True
            status = sell_status  # Update status to SELL

    # If no crossovers occurred, append neutral message
    if not ema_cross_flag:
        signals.append("⚪ *No EMA crosses detected.* Market is sideways.")

    return signals, status, ema_cross_flag  # Return signals, trade action, and crossover flag


def detect_support_resistance_sr(latest):
    """
    Check if the price is near key support or resistance levels.

    This function determines whether the price is:
    - Near support (potential buying opportunity).
    - Near resistance (potential selling pressure).
    - In a neutral zone (no strong support/resistance signals).

    Parameters:
    latest (dict): A dictionary containing the latest price and indicator values.

    Returns:
    tuple: A list of signals and a status string ("BUY", "SELL", or "HOLD").
    """
    signals = []
    status = "HOLD"

    # Check if the price is close to the support level (within 2% range)
    if latest["close"] <= latest["Support"] * 1.02:
        signals.append("🔵 *Price Near Support* → Buying Opportunity")
        status = "BUY"

    # Check if the price is close to the resistance level (within 2% range)
    elif latest["close"] >= latest["Resistance"] * 0.98:
        signals.append("🔴 *Price Near Resistance* → Potential selling pressure ahead!")
        status = "SELL"

    # If price is neither near support nor resistance, it's in a neutral zone
    else:
        signals.append("⚪ *Price in Neutral Zone* → No strong support/resistance signals.")
        status = "HOLD"

    return signals, status


def detect_breakouts(df):
    """
    Identify breakouts with ATR filtering to avoid weak signals.

    - Bullish Breakout: Close above resistance with high volume & breakout > 1.5x ATR.
    - Bearish Breakdown: Close below support with strong selling pressure & breakdown > 1.5x ATR.

    ATR is used to measure breakout strength and set dynamic stop-loss & take-profit targets.
    """
    df = util_indicators.detect_support_resistance(df)  # Ensure S/R levels are available
    df = util_indicators.calculate_atr(df)  # Calculate ATR for volatility filtering
    # print(" detect_breakouts Available columns:", df.columns)
    df["Prev_Close"] = df["close"].shift(1)  # Previous closing price for comparison
    df["Avg_Volume"] = df["volume"].rolling(20).mean()  # Calculate average volume over 20 periods

    signals = []
    latest = df.iloc[-1]  # Get the most recent data point
    status = "HOLD"

    # Define ATR-based filtering threshold (e.g., 1.5x ATR)
    atr_threshold = 1.5 * latest["ATR"] if pd.notna(latest["ATR"]) else 0

    # Bullish Breakout:
    # - Price closed above resistance
    # - Previous close was below resistance (confirmation)
    # - Volume is above average (strong momentum)
    # - Breakout strength > ATR threshold (filters out weak moves)
    if latest["close"] > latest["Resistance"] and latest["Prev_Close"] <= latest["Resistance"] \
            and latest["volume"] > latest["Avg_Volume"] and (latest["close"] - latest["Resistance"]) > atr_threshold:

        stop_loss = latest["Resistance"] - latest["ATR"]  # Dynamic stop-loss below resistance
        take_profit = latest["close"] + (2 * latest["ATR"])  # Take profit at 2x ATR

        signals.append(f"🚀 *Bullish Breakout!* Price closed above resistance with high volume.\n"
                       f"🔹 Entry: {latest['close']:.2f}\n"
                       f"🔸 Stop-Loss: {stop_loss:.2f}\n"
                       f"🎯 Take-Profit: {take_profit:.2f}")
        status = "BUY"

    # Bearish Breakdown:
    # - Price closed below support
    # - Previous close was above support (confirmation)
    # - Volume is above average (strong selling pressure)
    # - Breakdown strength > ATR threshold (filters weak moves)
    elif latest["close"] < latest["Support"] and latest["Prev_Close"] >= latest["Support"] \
            and latest["volume"] > latest["Avg_Volume"] and (latest["Support"] - latest["close"]) > atr_threshold:

        stop_loss = latest["Support"] + latest["ATR"]  # Dynamic stop-loss above support
        take_profit = latest["close"] - (2 * latest["ATR"])  # Take profit at 2x ATR

        signals.append(f"⚠️ *Bearish Breakdown!* Price dropped below support with strong selling pressure.\n"
                       f"🔹 Entry: {latest['close']:.2f}\n"
                       f"🔸 Stop-Loss: {stop_loss:.2f}\n"
                       f"🎯 Take-Profit: {take_profit:.2f}")

        status = "SELL"

    # No breakout detected
    else:
        signals.append(
            "⚪ *No breakout detected.* Price is still within the support/resistance range, indicating consolidation.")

    return [signals, status]


def detect_trend(df):
    """
    Detects the market trend based on EMA alignment and ADX strength.

    The function analyzes the relationship between the 50, 100, and 200-period
    Exponential Moving Averages (EMA) to determine whether the market is in an uptrend,
    downtrend, or ranging condition. The ADX (Average Directional Index) is used to
    confirm trend strength.

    Parameters:
    df (DataFrame): Historical price data containing OHLCV.

    Returns:
    list: A formatted message describing the detected trend.
    """

    # Compute key EMAs for trend analysis
    df["EMA50"] = util_indicators.calculate_ema(df, 50)  # Short-to-mid-term trend
    df["EMA100"] = util_indicators.calculate_ema(df, 100)  # Mid-to-long-term trend
    df["EMA200"] = util_indicators.calculate_ema(df, 200)  # Long-term trend
    df["ADX"] = util_indicators.calculate_adx(df)  # Trend strength indicator

    latest = df.iloc[-1]  # Get the most recent data point
    trend = "Neutral / No Clear Trend"  # Default trend message
    trend_status = "Neutral"
    """
    Uptrend
    Downtrend
    """

    # Check for an uptrend: EMA50 > EMA100 > EMA200
    if latest["EMA50"] > latest["EMA100"] > latest["EMA200"]:
        if latest["ADX"] > 25:
            trend = "📈 *Strong Uptrend* → High momentum, trend continuation likely!"
            trend_status = "Strong Uptrend"
        elif latest["ADX"] > 20:
            trend = "📊 *Moderate Uptrend* → Bullish bias, but not very strong."
            trend_status = "Moderate Uptrend"
        else:
            trend = "🟢 *Weak Uptrend* → Price trending up, but with low conviction."
            trend_status = "Weak Uptrend"

    # Check for a downtrend: EMA50 < EMA100 < EMA200
    elif latest["EMA50"] < latest["EMA100"] < latest["EMA200"]:
        if latest["ADX"] > 25:
            trend = "📉 *Strong Downtrend* → High momentum, trend continuation likely!"
            trend_status = "Strong Downtrend"
        elif latest["ADX"] > 20:
            trend = "📊 *Moderate Downtrend* → Bearish bias, but not very strong."
            trend_status = "Moderate Downtrend"
        else:
            trend = "🔴 *Weak Downtrend* → Price trending down, but with low conviction."
            trend_status = "Weak Downtrend"

    # If ADX is below 20, market is weak or ranging
    elif latest["ADX"] < 20:
        trend = "⚪ *Sideways / Ranging Market* → Weak trend, avoid breakout trades."

    # return [trend]
    return [f"\n📊*Trend Analysis*:\n{trend}", trend_status]


def detect_rsi_signals(latest, trend_status):
    """
    Analyze RSI levels and generate buy/sell signals based on trend conditions.

    RSI thresholds are adjusted dynamically:
    - In a strong uptrend, the buy threshold is raised to 40 (instead of 30) to avoid premature entries.
    - In a strong downtrend, the sell threshold is lowered to 60 (instead of 70) to allow earlier exits.

    Parameters:
    latest (dict): Most recent price data containing RSI.
    trend_status (str): Current market trend (e.g., "Strong Uptrend", "Neutral", "Strong Downtrend").

    Returns:
    tuple:
        - signals (list): List of formatted messages indicating detected RSI conditions.
        - status (str): The overall trading action determined (BUY, SELL, or HOLD).
    """
    signals = []
    status = "HOLD"

    # Ensure RSI data is available
    rsi_value = latest.get("RSI")
    if rsi_value is None:
        return ["⚠️ *RSI data unavailable*"], status

    # Dynamic RSI thresholds based on trend strength
    if trend_status in ["Strong Uptrend", "Moderate Uptrend"]:
        rsi_buy_threshold = 40
    else:
        rsi_buy_threshold = 30  # Default buy threshold

    if trend_status in ["Strong Downtrend", "Moderate Downtrend"]:
        rsi_sell_threshold = 60
    else:
        rsi_sell_threshold = 70  # Default sell threshold

    # Detect overbought (SELL) condition
    if rsi_value > rsi_sell_threshold:
        signals.append(f"🔴 *RSI {rsi_value:.2f} > {rsi_sell_threshold} → Overbought! Potential Sell Signal*")
        status = "SELL"

    # Detect oversold (BUY) condition
    elif rsi_value < rsi_buy_threshold:
        signals.append(f"🟢 *RSI {rsi_value:.2f} < {rsi_buy_threshold} → Oversold! Potential Buy Signal*")
        status = "BUY"

    # If RSI is neutral (between thresholds), add a consolidation message
    else:
        signals.append(f"⚪ *RSI {rsi_value:.2f} is neutral → No strong buy/sell signal*")

    return signals, status


def get_market_sentiment(symbol):
    """
    Fetches Binance funding rates and determines market sentiment.

    Funding rates provide insight into trader positioning:
    - **Positive funding rates** → More long positions → Potential overbought conditions.
    - **Negative funding rates** → More short positions → Potential oversold conditions.

    Parameters:
    symbol (str): The trading pair (e.g., "BTCUSDT", "ETHUSDT").

    Returns:
    str: Market sentiment based on funding rates.
    """
    try:
        # Fetch the latest funding rates from Binance API
        funding_rates = util_gen.fetch_binance_funding_rates(symbol)

        # Ensure we have valid funding rate data
        if funding_rates is None:
            return "⚠️ *Market Sentiment: Data Unavailable* (Failed to fetch funding rates)"

        # Analyze funding rate data to determine sentiment
        sentiment = analyze_market_sentiment(funding_rates)

    except Exception as e:
        return f"⚠️ *Market Sentiment: Error* (Failed to retrieve funding rates: {str(e)})"

    return sentiment


def analyze_market_sentiment(funding_rates):
    """
    Analyze Binance funding rates to determine overall market sentiment using statistical thresholds.

    Parameters:
    funding_rates (list or DataFrame): A list of dictionaries containing funding rate data from Binance.

    Returns:
    str: A formatted message summarizing the market sentiment based on funding rates.
    """
    # Handle incorrect data types
    if isinstance(funding_rates, str):
        try:
            funding_rates = json.loads(funding_rates)  # Convert JSON string to list
        except json.JSONDecodeError:
            return "❓ *Market Sentiment*: Invalid data format received."

    if isinstance(funding_rates, pd.DataFrame):
        funding_rates = funding_rates.to_dict('records')  # Convert DataFrame to list of dictionaries

    if not isinstance(funding_rates, list) or not funding_rates:
        return "❓ *Market Sentiment*: Data Unavailable"

    # Convert funding rates to floats and calculate mean & standard deviation
    try:
        funding_values = [float(rate["fundingRate"]) for rate in funding_rates]
    except (KeyError, TypeError, ValueError):
        return "❓ *Market Sentiment*: Invalid funding rate data."

    avg_funding_rate = sum(funding_values) / len(funding_values)
    std_dev = (sum((x - avg_funding_rate) ** 2 for x in funding_values) / len(funding_values)) ** 0.5

    # Define thresholds dynamically based on standard deviation
    strong_threshold = avg_funding_rate + std_dev  # Significantly above average
    weak_threshold = avg_funding_rate - std_dev  # Significantly below average

    # Determine sentiment based on funding rate levels
    if avg_funding_rate > strong_threshold:
        sentiment = "🟢 *Strong Bullish Sentiment:* High demand for long positions. Traders expect higher prices."
    elif avg_funding_rate > 0:
        sentiment = "🟩 *Moderate Bullish Sentiment:* More long positions than shorts, indicating mild optimism."
    elif avg_funding_rate < weak_threshold:
        sentiment = "🔴 *Strong Bearish Sentiment:* Shorts are dominant. Traders expect prices to decline."
    elif avg_funding_rate < 0:
        sentiment = "🟥 *Moderate Bearish Sentiment:* More short positions than longs, showing cautious pessimism."
    else:
        sentiment = "⚪ *Neutral Market:* Balanced long and short positions, no clear directional bias."

    # return f"\n📊 *Binance Funding Rate Analysis:* \n{sentiment} \n*Avg Rate:* {avg_funding_rate:.6f} (Std Dev: {std_dev:.6f})"
    return f"\n📊 *Binance Funding Rate Analysis:* \n{sentiment}"


def detect_whale_activity(df):
    """
    Detect whale activity based on sudden spikes in trading volume.

    Why it matters:
    - Whales (large investors) buy before big rallies and sell before crashes.
      Detecting their activity can provide early warning signals for price swings.
    - Low-volume breakouts are often fakeouts—whales may trap retail traders before selling off.

    Parameters:
    df (DataFrame): The historical market data containing volume, close, and open prices.

    Returns:
    str: A formatted alert message indicating whale activity (or none if no activity detected).
    """

    # Compute the moving average of volume (20-period) for reference
    df["volume_ma"] = df["volume"].rolling(window=20).mean()

    # Ensure volume is in float format for calculations
    df["volume"] = df["volume"].astype(float)

    # Detect volume spikes (if volume is 2.5 times greater than the moving average)
    df["volume_spike"] = df["volume"] > 2.5 * df["volume_ma"]

    # Get the most recent row (latest market data point)
    latest_row = df.iloc[-1]

    # Default alert message (no whale activity detected)
    alert_message = "🐋 *Whale activity*: NONE"

    # If a volume spike is detected, generate an alert
    if latest_row["volume_spike"]:
        alert_message = f"🐋 *Whale Activity Detected!* 🐋\n\n"
        alert_message += f"*Volume Spike:* {latest_row['volume']:.2f} (Avg: {latest_row['volume_ma']:.2f})\n"
        alert_message += f"*Time:* {latest_row['timestamp']}\n"

        # Determine buy/sell pressure based on price movement
        if float(latest_row["close"]) > float(latest_row["open"]):
            alert_message += "🟢 *Large Buy Activity!*"  # Price closed higher (buying pressure)
        else:
            alert_message += "🔴 *Large Sell Activity!*"  # Price closed lower (selling pressure)

    return f"\n{alert_message}"
