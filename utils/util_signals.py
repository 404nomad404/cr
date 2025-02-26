# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

__author__ = 'Ishafizan'
__date__ = "15 Feb 2025"

import pandas as pd
import json
from utils import util_gen, util_indicators
import settings
from utils.util_log import logger

# Initialize logger for debugging and tracking
log = logger()


def determine_trade_signal(log, ema_confirmation, rsi_confirmation, support_resistance_confirmation,
                           breakout_confirmation, macd_confirmation, wvix_stoch_confirmation,
                           trend_status, latest):
    config = settings.TREND_CONFIG[settings.MIN_TREND_STRENGTH]
    adx_threshold = config["ADX_THRESHOLD"]

    adx_value = latest.get("ADX", 0)
    high_volume = latest["volume"] > latest["Volume_MA"]
    price_change = ((latest["close"] - latest.get("Prev_Close", latest["close"])) /
                    latest.get("Prev_Close", latest["close"])) * 100 if latest.get("Prev_Close") else 0

    valid_trends = {
        "Weak": ["Strong Uptrend", "Strong Downtrend", "Moderate Uptrend", "Weak Uptrend", "Moderate Downtrend",
                 "Weak Downtrend"],
        "Moderate": ["Strong Uptrend", "Strong Downtrend", "Moderate Uptrend", "Moderate Downtrend"],
        "Strong": ["Strong Uptrend", "Strong Downtrend"]
    }
    adx_trend = trend_status in valid_trends[settings.MIN_TREND_STRENGTH]

    confirmations = [
        ("EMA", ema_confirmation, "BUY" if ema_confirmation else None),
        ("RSI", rsi_confirmation, "BUY" if rsi_confirmation else None),
        ("S/R", support_resistance_confirmation, "BUY" if support_resistance_confirmation else None),
        ("Breakout", breakout_confirmation, "BUY" if breakout_confirmation else None),
        ("MACD", macd_confirmation, "SELL" if macd_confirmation else None),
        ("WVIX/Stoch", wvix_stoch_confirmation, "BUY" if wvix_stoch_confirmation else None)
    ]
    buy_count = sum(1 for _, conf, direction in confirmations if conf and direction == "BUY")
    sell_count = sum(1 for _, conf, direction in confirmations if conf and direction == "SELL")

    log.info(f"Initial buy_count: {buy_count}, sell_count: {sell_count}, price_change: {price_change:.2f}%, "
             f"adx_trend: {adx_trend}, high_volume: {high_volume}")

    # Boost SELL only for downtrends
    if macd_confirmation and trend_status in ["Strong Downtrend", "Moderate Downtrend"] and adx_value > adx_threshold:
        sell_count += 1
        if price_change < -3 and high_volume:
            sell_count += 1

    # Boost BUY only for uptrends
    if wvix_stoch_confirmation and trend_status in ["Strong Uptrend", "Moderate Uptrend"] and adx_value > adx_threshold:
        buy_count += 1
        if price_change > 3 and high_volume:
            buy_count += 1

    log.info(f"Adjusted buy_count: {buy_count}, sell_count: {sell_count}")

    if sell_count >= 2:
        strength = "Strong" if sell_count >= 3 or adx_value > 30 else "Moderate"
        if adx_value > adx_threshold and high_volume:
            message = "🚨 SELL - Strong Downtrend with High Volume & ADX Confirmation"
        elif adx_value > adx_threshold:
            message = "❌ SELL - Downtrend Confirmed with Strong ADX"
        else:
            message = "SELL - Proceed with Caution"
        action = "SELL"
    elif buy_count >= 2 or (wvix_stoch_confirmation and buy_count >= 1):
        strength = "Strong" if buy_count >= 3 or adx_value > 30 else "Moderate"
        if wvix_stoch_confirmation:
            message = "🔥 BUY - Potential Bottom with WVIX/Stochastic Confirmation"
            if adx_value > adx_threshold and high_volume:
                message += " + Strong Uptrend, High Volume & ADX"
            elif adx_value > adx_threshold:
                message += " + Strong ADX"
            elif high_volume:
                message += " + High Volume"
        elif adx_value > adx_threshold and high_volume:
            message = "🔥 BUY - Strong Uptrend with High Volume & ADX Confirmation"
        elif adx_value > adx_threshold:
            message = "✅ BUY - Uptrend Confirmed with Strong ADX"
        elif high_volume:
            message = "📈 BUY - Uptrend Confirmed with High Volume"
        else:
            message = "🟡 BUY - Proceed with Caution"
        action = "BUY"
    else:
        action = "HOLD"
        if wvix_stoch_confirmation:
            message = "⚠️ HOLD → WVIX/Stochastic Bottom Detected but Insufficient Other Confirmations"
        elif sell_count == 1 or buy_count == 1:
            message = "⚠️ HOLD → Insufficient confirmation from other indicators"
        elif not adx_trend:
            message = "⚠️ HOLD → Trend not strong enough"
        else:
            message = "⚠️ HOLD → No strong confirmation from other indicators"
        strength = "Weak"

    log.info(f"determine_trade_signal: action: {action}, strength: {strength}, message: {message}")
    return {"action": action, "strength": strength, "message": message}


def detect_ema_crossovers(log, latest, previous):
    """
    Detects Exponential Moving Average (EMA) crossovers to identify potential trend reversals or continuations.

    Uses ADX and volume to confirm the strength of detected crossovers, based on trend strength settings in config.
    - Bullish crossover: Short EMA crosses above long EMA (BUY signal).
    - Bearish crossover: Short EMA crosses below long EMA (SELL signal).

    Args:
        log: Logger instance for tracking crossover events.
        latest (pd.Series): Latest candlestick data with EMAs, ADX, and volume.
        previous (pd.Series): Previous candlestick data for comparison.

    Returns:
        tuple: (signals, status, ema_cross_flag)
            - signals (list): Formatted messages describing detected crossovers.
            - status (str): Trade action ("BUY", "SELL", "HOLD").
            - ema_cross_flag (bool): True if a crossover occurred, False otherwise.
    """
    signals = []
    ema_cross_flag = False
    status = "HOLD"

    # Load trend configuration dynamically
    config = settings.TREND_CONFIG[settings.MIN_TREND_STRENGTH]

    # Extract confirmation metrics
    adx_value = latest.get("ADX", 0)  # ADX for trend strength
    adx_threshold = config["ADX_THRESHOLD"]  # Threshold from config
    high_volume = latest["volume"] > latest["Volume_MA"]  # Volume above moving average

    # Define EMA crossover conditions based on configurable periods
    crossover_conditions = []
    ema_periods = sorted(config["EMA_PERIODS"])  # Ensure short EMA precedes long EMA

    for i in range(len(ema_periods) - 1):
        short_ema, long_ema = f"EMA{ema_periods[i]}", f"EMA{ema_periods[i + 1]}"
        bullish_msg = f"📈 *{short_ema} crossed above {long_ema}*"
        bearish_msg = f"📉 *{short_ema} crossed below {long_ema}*"
        crossover_conditions.append((short_ema, long_ema, bullish_msg, bearish_msg, "BUY", "SELL"))

    # Add Golden/Death Cross if EMA100 and EMA200 are in config
    if "EMA100" in [f"EMA{p}" for p in ema_periods] and "EMA200" in [f"EMA{p}" for p in ema_periods]:
        crossover_conditions.append(("EMA100", "EMA200", "✅ *EMA100 crossed above EMA200 (Golden Cross)*",
                                     "❌ *EMA100 crossed below EMA200 (Death Cross)*", "BUY", "SELL"))

    # Check each crossover condition
    for short_ema, long_ema, bullish_msg, bearish_msg, buy_status, sell_status in crossover_conditions:
        if short_ema not in latest or long_ema not in latest or short_ema not in previous or long_ema not in previous:
            continue  # Skip if required EMA data is missing

        # Detect bullish (upward) and bearish (downward) crossovers
        bullish_crossover = latest[short_ema] > latest[long_ema] and previous[short_ema] <= previous[long_ema]
        bearish_crossover = latest[short_ema] < latest[long_ema] and previous[short_ema] >= previous[long_ema]

        latest_date = latest.name if hasattr(latest, "name") else "UNKNOWN_DATE"

        if bullish_crossover:
            msg = bullish_msg
            if adx_value > adx_threshold:
                msg += f" 🔥 (Confirmed by ADX > {adx_threshold})"
            if high_volume:
                msg += " 🚀 (Confirmed by High Volume)"
            msg += f"\n🚀 BUY SIGNAL: {bullish_msg} at price {latest['close']:.2f} on {latest_date}"
            log.info(msg)
            signals.append(msg)
            ema_cross_flag = True
            status = buy_status

        if bearish_crossover:
            msg = bearish_msg
            if adx_value > adx_threshold:
                msg += f" 🔴 Confirmed by ADX > {adx_threshold}"
            if high_volume:
                msg += " 🔴 Confirmed by High Volume"
            msg += f"\n🔻 SELL SIGNAL: {bearish_msg} at price {latest['close']:.2f} on {latest_date}"
            log.info(msg)
            signals.append(msg)
            ema_cross_flag = True
            status = sell_status

    # Indicate no crossover if none detected
    if not ema_cross_flag:
        signals.append("⚪ *No EMA crosses detected.* Market is sideways.")

    return signals, status, ema_cross_flag


def detect_support_resistance_sr(latest):
    """
    Identifies proximity to support or resistance levels, tying BUY signals to WVIX/Stochastic confirmation.

    Args:
        latest (dict): Latest price data with 'close', 'Support', and 'Resistance' values.

    Returns:
        tuple: (signals, status)
    """
    signals = []
    status = "HOLD"

    if latest["close"] <= latest["Support"] * 1.02:
        signals.append(f"🔵 *Support Zone:* Near {latest['Support'] * 1.02:.2f} - Watching for stabilization.")
        status = "HOLD"  # Wait for WVIX/Stochastic confirmation
    elif latest["close"] >= latest["Resistance"] * 0.98:
        signals.append(
            f"🔴 *Price Near Resistance:* ({latest['Resistance'] * 0.98:.2f}) → Potential selling pressure ahead!")
        status = "SELL"
    else:
        signals.append("⚪ *Price in Neutral Zone* → No strong support/resistance signals.")
        status = "HOLD"

    return signals, status


def detect_breakouts(df):
    """
    Detects price breakouts above resistance or below support, confirmed by ATR and volume.

    - Bullish Breakout: Price exceeds resistance by breakout percentage (BUY).
    - Bearish Breakdown: Price drops below support by breakout percentage (SELL).
    - Includes stop-loss and take-profit levels based on ATR.

    Args:
        df (pd.DataFrame): Historical data with OHLCV and calculated indicators.

    Returns:
        list: [signals, status]
            - signals (list): Messages with breakout details and trade levels.
            - status (str): Trade action ("BUY", "SELL", "HOLD").
    """
    config = settings.TREND_CONFIG[settings.MIN_TREND_STRENGTH]
    breakout_percent = config["BREAKOUT_PERCENTAGE"]
    volume_multiplier = config["VOLUME_MULTIPLIER"]
    atr_multiplier = config["ATR_MULTIPLIER"]

    # Prepare dataframe with required indicators
    df = util_indicators.detect_support_resistance(df)
    df = util_indicators.calculate_atr(df)
    df["Prev_Close"] = df["close"].shift(1)
    df["Avg_Volume"] = df["volume"].rolling(20).mean()

    signals = []
    latest = df.iloc[-1]
    status = "HOLD"

    if pd.isna(latest["ATR"]):
        signals.append("⚠️ ATR data unavailable for breakout analysis.")
        return [signals, status]

    atr_threshold = atr_multiplier * latest["ATR"]

    # Check for bullish breakout
    if latest["close"] > latest["Resistance"] * (1 + breakout_percent):
        if util_indicators.check_breakout(latest["close"], latest["Resistance"], "BUY", latest, atr_threshold,
                                          volume_multiplier):
            status = "BUY"
            bullish_stop_loss = latest["Resistance"] - (latest["ATR"] * atr_multiplier)
            bullish_take_profit = latest["close"] + (2 * latest["ATR"] * atr_multiplier)
            signals.append(
                generate_breakout_message(latest["close"], latest["Resistance"], "BUY", latest, volume_multiplier,
                                          atr_threshold))
            signals.append(f"🔹 Entry: {latest['close']:.2f}\n"
                           f"🔸 Stop-Loss: {bullish_stop_loss:.2f}\n"
                           f"🎯 Take-Profit: {bullish_take_profit:.2f}")

    # Check for bearish breakdown
    elif latest["close"] < latest["Support"] * (1 - breakout_percent):
        if util_indicators.check_breakout(latest["close"], latest["Support"], "SELL", latest, atr_threshold,
                                          volume_multiplier):
            status = "SELL"
            bearish_stop_loss = latest["Support"] + (latest["ATR"] * atr_multiplier)
            bearish_take_profit = latest["close"] - (2 * latest["ATR"] * atr_multiplier)
            signals.append(
                generate_breakout_message(latest["close"], latest["Support"], "SELL", latest, volume_multiplier,
                                          atr_threshold))
            signals.append(f"🔹 Entry: {latest['close']:.2f}\n"
                           f"🔸 Stop-Loss: {bearish_stop_loss:.2f}\n"
                           f"🎯 Take-Profit: {bearish_take_profit:.2f}")

    else:
        signals.append("  • ⚪ *No breakout detected.* Price within the S/R range, indicating consolidation.")

    return [signals, status]


def generate_breakout_message(price, level, direction, latest, volume_multiplier, atr_threshold):
    """
    Creates a descriptive message for a breakout event with confirmation details.

    Args:
        price (float): Current price.
        level (float): Support or resistance level breached.
        direction (str): "BUY" for bullish, "SELL" for bearish.
        latest (pd.Series): Latest data with volume and ATR.
        volume_multiplier (float): Volume confirmation threshold.
        atr_threshold (float): ATR confirmation threshold.

    Returns:
        str: Formatted breakout message with confirmation status.
    """
    base_message = f"🚀 *{'Bullish Breakout' if direction == 'BUY' else 'Bearish Breakdown'}!* Price closed {abs((price - level) / level) * 100:.2f}% {'above resistance' if direction == 'BUY' else 'below support'}."
    volume_confirmed = latest["volume"] > (latest["Avg_Volume"] * volume_multiplier)
    price_move = abs(latest["close"] - level) if direction == "BUY" else abs(level - latest["close"])
    atr_confirmed = price_move > atr_threshold

    if volume_confirmed and atr_confirmed:
        return f"{base_message} - Confirmed with high volume and strong ATR."
    elif volume_confirmed:
        return f"{base_message} - Confirmed with high volume."
    elif atr_confirmed:
        return f"{base_message} - Confirmed with strong ATR."
    else:
        return f"{base_message} - Initial signs of breakout, but lacks volume or ATR confirmation."


def detect_trend(log, df):
    """
    Assesses market trend direction and strength using EMA alignment, ADX, and price direction.

    - Uptrend: EMA alignment or ADX > 25 with positive price change.
    - Downtrend: EMA alignment or ADX > 25 with negative price change.
    - Ranging: ADX < 20, no clear direction.

    Args:
        log: Logger instance for tracking.
        df (pd.DataFrame): Historical OHLCV data.

    Returns:
        list: [message, trend_status]
    """
    df["EMA9"] = util_indicators.calculate_ema(df, 9)
    df["EMA21"] = util_indicators.calculate_ema(df, 21)
    df["EMA50"] = util_indicators.calculate_ema(df, 50)
    df["EMA100"] = util_indicators.calculate_ema(df, 100)
    df["EMA200"] = util_indicators.calculate_ema(df, 200)
    df["ADX"] = util_indicators.calculate_adx(df)

    latest = df.iloc[-1]
    previous = df.iloc[-2] if len(df) > 1 else latest
    price_change = ((latest["close"] - previous["close"]) / previous["close"]) * 100 if previous["close"] != 0 else 0

    trend = "  • ⚪ *Neutral / No Clear Trend*"
    trend_status = "Neutral"

    # EMA alignment for uptrend
    if latest["EMA9"] > latest["EMA21"] > latest["EMA50"] > latest["EMA100"] > latest["EMA200"]:
        if latest["ADX"] > 25:
            trend = "  • 📈 *Strong Uptrend* → High momentum, likely continuation."
            trend_status = "Strong Uptrend"
        elif latest["ADX"] > 20:
            trend = "  • 📊 *Moderate Uptrend* → Bullish, but momentum lacks strength."
            trend_status = "Moderate Uptrend"
        else:
            trend = "  • 🟢 *Weak Uptrend* → Rising, but conviction is low."
            trend_status = "Weak Uptrend"
    # EMA alignment for downtrend
    elif latest["EMA9"] < latest["EMA21"] < latest["EMA50"] < latest["EMA100"] < latest["EMA200"]:
        if latest["ADX"] > 25:
            trend = "  • 📉 *Strong Downtrend* → High momentum, likely continuation."
            trend_status = "Strong Downtrend"
        elif latest["ADX"] > 20:
            trend = "  • 📊 *Moderate Downtrend* → Bearish, but momentum lacks strength."
            trend_status = "Moderate Downtrend"
        else:
            trend = "  • 🔴 *Weak Downtrend* → Falling, but conviction is low."
            trend_status = "Weak Downtrend"
    # Use ADX and price change when EMAs don’t align
    elif latest["ADX"] > 25:
        if price_change < 0:
            trend = "  • 📉 *Strong Downtrend* → High momentum, likely continuation."
            trend_status = "Strong Downtrend"
        elif price_change > 0:
            trend = "  • 📈 *Strong Uptrend* → High momentum, likely continuation."
            trend_status = "Strong Uptrend"
    elif latest["ADX"] > 20:
        if price_change < 0:
            trend = "  • 📊 *Moderate Downtrend* → Bearish, but momentum lacks strength."
            trend_status = "Moderate Downtrend"
        elif price_change > 0:
            trend = "  • 📊 *Moderate Uptrend* → Bullish, but momentum lacks strength."
            trend_status = "Moderate Uptrend"
    elif latest["ADX"] < 20:
        trend = "  • ⚪ *Ranging Market* → Weak trend, breakout trades risky."

    trend_score = util_indicators.calculate_trend_score(df)

    # Inline directional trend score interpretation
    direction = "downward" if price_change < 0 else "upward"
    if trend_score >= 75:
        trend_score_message = f"🚀 Strong Trend: Market gaining {direction} momentum, potential {direction} breakout."
    elif trend_score >= 50:
        trend_score_message = f"🟡 Moderate Trend: Steady {direction} movement, watch for confirmation."
    else:
        trend_score_message = "⚪ Weak Trend: Low momentum, ranging likely."

    message = f"\n📊*Trends*:\n{trend}\n  • ⚡*Trend Score:* {trend_score}/100 → {trend_score_message}"

    log.debug(f"Trend: {trend_status}, ADX={latest['ADX']:.2f}, price_change={price_change:.2f}%")
    return [message, trend_status]


def detect_rsi_signals(latest, trend_status):
    """
    Generates RSI-based signals, adjusting thresholds based on trend strength.

    Args:
        latest (dict): Latest price data with RSI value.
        trend_status (str): Current trend (e.g., "Strong Uptrend").

    Returns:
        tuple: (signals, status)
    """
    """
    signals = []
    status = "HOLD"

    rsi_value = latest.get("RSI")
    if rsi_value is None:
        return ["⚠️ *RSI data unavailable*"], status

    rsi_buy_threshold = 40 if trend_status in ["Strong Uptrend", "Moderate Uptrend"] else 30
    rsi_sell_threshold = 60 if trend_status in ["Strong Downtrend", "Moderate Downtrend"] else 70

    if rsi_value > rsi_sell_threshold:
        signals.append(f"🔴 *RSI {rsi_value:.2f} > {rsi_sell_threshold} → Overbought!* Potential Sell Signal")
        status = "SELL"
    elif rsi_value < rsi_buy_threshold:
        signals.append(f"🟢 *RSI {rsi_value:.2f} < {rsi_buy_threshold} → Oversold!* Potential Buy Signal")
        status = "BUY"
    else:
        signals.append(
            f"⚪ *RSI {rsi_value:.2f}* → {'Nearing oversold' if rsi_value < 35 else 'Neutral'} - No strong buy/sell signal")
        status = "HOLD"
    """
    # return signals, status
    return [], "HOLD"  # RSI moved to detect_wvix_stoch_signals


def get_market_sentiment(symbol, trend_status=None):
    """
    Fetches and interprets Binance funding rates to gauge market sentiment.

    Args:
        symbol (str): Trading pair (e.g., "BTCUSDT").
        trend_status (str): Current trend status for context (optional).

    Returns:
        str: Formatted sentiment message.
    """
    try:
        funding_rates = util_gen.fetch_binance_funding_rates(symbol)
        if funding_rates is None:
            return "⚠️ *Market Sentiment: Data Unavailable* (Failed to fetch funding rates)"
        sentiment = analyze_market_sentiment(funding_rates, trend_status)
    except Exception as e:
        return f"⚠️ *Market Sentiment: Error* (Failed to retrieve funding rates: {str(e)})"
    return sentiment


def analyze_market_sentiment(funding_rates, trend_status=None):
    """
    Analyzes funding rates to determine market sentiment with trend context.

    Args:
        funding_rates (list or pd.DataFrame): Funding rate data from Binance.
        trend_status (str): Current trend status (e.g., "Strong Downtrend") for context.

    Returns:
        str: Sentiment message with trend alignment.
    """
    if isinstance(funding_rates, str):
        try:
            funding_rates = json.loads(funding_rates)
        except json.JSONDecodeError:
            return "❓ *Market Sentiment*: Invalid data format received."

    if isinstance(funding_rates, pd.DataFrame):
        funding_rates = funding_rates.to_dict('records')

    if not isinstance(funding_rates, list) or not funding_rates:
        return "❓ *Market Sentiment*: Data Unavailable"

    try:
        funding_values = [float(rate["fundingRate"]) for rate in funding_rates]
    except (KeyError, TypeError, ValueError):
        return "❓ *Market Sentiment*: Invalid funding rate data."

    avg_funding_rate = sum(funding_values) / len(funding_values)
    std_dev = (sum((x - avg_funding_rate) ** 2 for x in funding_values) / len(funding_values)) ** 0.5

    strong_threshold = avg_funding_rate + std_dev
    weak_threshold = avg_funding_rate - std_dev
    neutral_threshold = 0.001  # 0.1% cutoff for negligible rates

    if abs(avg_funding_rate) < neutral_threshold:
        sentiment = "⚪ *Neutral Market:* Balanced positions."
    elif avg_funding_rate > strong_threshold:
        sentiment = "🟢 *Strong Bullish Sentiment:* High demand for long positions."
    elif avg_funding_rate > 0:
        sentiment = "🟩 *Moderate Bullish Sentiment:* More longs than shorts."
    elif avg_funding_rate < weak_threshold:
        sentiment = "🔴 *Strong Bearish Sentiment:* Shorts dominant."
    elif avg_funding_rate < 0:
        sentiment = "🟥 *Moderate Bearish Sentiment:* More shorts than longs."

    # Add trend context if provided
    if trend_status and "Downtrend" in trend_status and avg_funding_rate > 0:
        sentiment += " (Contrarian: Bullish sentiment in a downtrend may signal potential reversal or squeeze.)"
    elif trend_status and "Uptrend" in trend_status and avg_funding_rate < 0:
        sentiment += " (Contrarian: Bearish sentiment in an uptrend may signal potential reversal or squeeze.)"

    # Include funding rate value
    return f"\n📊 *Binance Funding Rate:*\n  • {sentiment} Avg Rate: {avg_funding_rate:.4f}%"


def detect_whale_activity(df, symbol="BTCUSDT"):
    """
    Detects whale activity using Binance volume spikes and BTC-specific Blockchair transactions.

    Args:
        df (pd.DataFrame): Historical OHLCV data.
        symbol (str): Trading pair (e.g., "BTCUSDT").

    Returns:
        str: Formatted message summarizing whale activity.
    """
    config = settings.TREND_CONFIG[settings.MIN_TREND_STRENGTH]
    signals = []

    df["volume_ma"] = df["volume"].rolling(window=20).mean()
    df["volume"] = df["volume"].astype(float)
    df["volume_spike"] = df["volume"] > config["VOLUME_MULTIPLIER"] * df["volume_ma"]
    latest_row = df.iloc[-1]

    if latest_row["volume_spike"]:
        spike_msg = (
            f"  • 🐳 *Volume Spike Detected!*\n"
            f"  • Volume: {latest_row['volume']:.2f} (Avg: {latest_row['volume_ma']:.2f})\n"
            f"  • Time: {latest_row.name}\n"
            f"  • {'🟢 Large Buy' if float(latest_row['close']) > float(latest_row['open']) else '🔴 Large Sell'} Activity!"
        )
        signals.append(spike_msg)

    base_symbol = symbol[:-4]

    if symbol == "BTCUSDT":
        try:
            whale_txns = util_gen.fetch_blockchair_whale_txns(min_value=1000)
            if whale_txns:
                for txn in whale_txns[:5]:
                    if txn["amount"] > 0:
                        direction = "Accumulation" if not any(
                            "exchange" in output.get("type", "") for output in txn["to"]) else "Sell-Off"
                        signals.append(f"🐳 *{base_symbol} Whale Move*: {txn['amount']:.2f} BTC → {direction}")
            else:
                signals.append(f"⚪ No significant {base_symbol} whale transactions *(Blockchair)*")
        except Exception as e:
            signals.append(f"⚠️ *Blockchair Error for {base_symbol}*: {str(e)}")

    try:
        binance_vol = util_gen.fetch_binance_volume(symbol=symbol)
        if not binance_vol.empty and len(binance_vol) >= 2:
            latest_vol = binance_vol["volume"].iloc[-1]
            prev_vol = binance_vol["volume"].iloc[-2]
            vol_increase = (latest_vol - prev_vol) / prev_vol * 100 if prev_vol > 0 else 0
            if vol_increase > 50:
                signals.append(
                    f"  • 📈 *Significant Volume Increase ({base_symbol})*: {vol_increase:.2f}% from previous day - Possible whale selling.")
            elif vol_increase < -50:
                signals.append(
                    f"  • 📉 *Significant Volume Drop ({base_symbol})*: {abs(vol_increase):.2f}% from previous day.")
            else:
                signals.append(f"  • ⚪ No significant volume activity for {base_symbol} *(Binance)*")
    except Exception as e:
        signals.append(f"  • ⚠️ *Binance Volume Error for {base_symbol}*: {str(e)}")

    if not signals:
        whale_message = f"\n🐋 *Whale Activity ({base_symbol})*: No significant activity detected"
    else:
        whale_message = f"\n🐋 *Whale Activity ({base_symbol}):*\n" + "\n".join(signals)

    return whale_message


def calculate_signal_strength(ema_confirmation, rsi_confirmation, support_resistance_confirmation,
                              breakout_confirmation, adx_trend, macd_confirmation):
    """
    Evaluates signal strength based on the number of confirming indicators.

    - 4+: Very Strong
    - 3: Strong
    - 2: Medium
    - 0-1: Weak

    Args:
        ema_confirmation (bool): EMA crossover signal.
        rsi_confirmation (bool): RSI overbought/oversold signal.
        support_resistance_confirmation (bool): S/R proximity signal.
        breakout_confirmation (bool): Breakout signal.
        adx_trend (bool): ADX trend strength confirmation.
        macd_confirmation (bool): MACD crossover signal.

    Returns:
        str: Signal strength ("Very Strong", "Strong", "Medium", "Weak").
    """
    confirmation_count = sum([ema_confirmation, rsi_confirmation, support_resistance_confirmation,
                              breakout_confirmation, adx_trend, macd_confirmation])

    if confirmation_count >= 4:
        return "Very Strong"
    elif confirmation_count >= 3:
        return "Strong"
    elif confirmation_count == 2:
        return "Medium"
    else:
        return "Weak"


def determine_adx_signal(latest, trend_status):
    """
    Assesses trend strength using ADX and volume data.

    - ADX < 20: Weak trend.
    - ADX > threshold: Strong trend, enhanced by high volume.

    Args:
        latest (dict): Latest data with ADX and volume.
        trend_status (str): Current trend status.

    Returns:
        str: Formatted ADX strength message.
    """
    config = settings.TREND_CONFIG[settings.MIN_TREND_STRENGTH]
    adx_value = latest.get("ADX", 0)
    high_volume = latest["volume"] > latest["Volume_MA"]

    if adx_value < 20:
        status_message = f" • 📉 *ADX*: {adx_value:.2f} → Weak trend, ranging market.\n"
    elif adx_value > config["ADX_THRESHOLD"] and high_volume:
        status_message = f" • 📈 *ADX*: {adx_value:.2f} → Strong trend confirmed with high volume.\n"
    elif adx_value > config["ADX_THRESHOLD"]:
        status_message = f" • 📊 *ADX*: {adx_value:.2f} → Strong trend detected, but volume is average.\n"
    elif 20 <= adx_value <= 25:
        status_message = f" • 🔄 *ADX*: {adx_value:.2f} → Moderate trend strength, possible breakout or consolidation.\n"
    else:
        status_message = f"NONE\n"

    return status_message


def interpret_trend_score(score):
    """
    Interprets the trend score into a descriptive message.

    Args:
        score (int): Trend score (0-100).

    Returns:
        str: Trend strength description.
    """
    if score <= 20:
        return "⚠️ *Very Weak Trend:* Choppy price action, low momentum."
    elif 21 <= score <= 40:
        return "📉 *Weak Trend:* Market is ranging, low conviction."
    elif 41 <= score <= 60:
        return "📊 *Moderate Trend:* Potential setups forming, watch closely."
    elif 61 <= score <= 80:
        return "🚀 *Strong Trend:* Market gaining momentum, potential breakout."
    else:
        return "🔥 *Very Strong Trend:* Strong momentum, high confidence in direction!"


def detect_macd_signal(log, df):
    """
    Detects MACD signals for trend direction and momentum shifts.

    - Bullish: MACD > Signal (BUY), enhanced by momentum shift.
    - Bearish: MACD < Signal (SELL), enhanced by momentum shift.

    Args:
        log: Logger instance.
        df (pd.DataFrame): Data with MACD indicators.

    Returns:
        tuple: (signal description, status)
    """
    df = util_indicators.calculate_macd(df)
    latest_macd = df.iloc[-1]["MACD_Line"]
    latest_signal = df.iloc[-1]["Signal_Line"]
    prev_macd = df.iloc[-2]["MACD_Line"]
    prev_signal = df.iloc[-2]["Signal_Line"]

    macd_histogram = latest_macd - latest_signal
    prev_histogram = prev_macd - prev_signal
    momentum_shift = (macd_histogram > 0 and prev_histogram < 0) or (macd_histogram < 0 and prev_histogram > 0)

    if latest_macd > latest_signal:
        if momentum_shift:
            return "⚡ MACD Bullish Momentum Shift - Early Uptrend Signal", "BUY"
        return "📈 MACD Bullish Crossover - Uptrend", "BUY"
    elif latest_macd < latest_signal:
        if momentum_shift:
            return "⚡ MACD Bearish Momentum Shift - Early Downtrend Signal", "SELL"
        return "📉 MACD Bearish Crossover - Downtrend", "SELL"
    else:
        return "⚖ MACD Neutral - No strong trend confirmation", "HOLD"


def generate_trend_momentum_message(log, ema_signals, ema_status, ema_cross_flag, macd_signals, macd_status,
                                    adx_signals, price_change=None):
    """
    Generates a formatted message for trend and momentum signals.

    Args:
        log: Logger instance.
        ema_signals (list): EMA crossover signals.
        ema_status (str): EMA signal status.
        ema_cross_flag (bool): EMA crossover flag.
        macd_signals (list or str): MACD signals.
        macd_status (str): MACD status.
        adx_signals (list): ADX signals.
        price_change (float): 24-hour price change percentage.

    Returns:
        str: Formatted trend and momentum message.
    """
    formatted_signals = ["📡 *Trend & Momentum:*"]

    # Helper to strip leading bullets
    def clean_signal(signal):
        if isinstance(signal, str):
            return signal.strip().lstrip(" •").strip()
        return str(signal)

    # Always include price change
    if price_change is not None:
        price_movement = (f"📈 *Price Movement:* {price_change:.2f}% in 24h" if price_change >= 0
                          else f"📉 *Price Movement:* {price_change:.2f}% in 24h")
        formatted_signals.append(price_movement)
        log.debug(f"Price movement added to Trend & Momentum: {price_movement}")

    # EMA and MACD summary
    if ema_cross_flag:
        formatted_signals.extend(
            [clean_signal(s) for s in (ema_signals if isinstance(ema_signals, list) else [ema_signals])])
    elif macd_status == "SELL":
        formatted_signals.append("⚪ No EMA cross, MACD confirms ongoing downtrend.")
    elif macd_status == "BUY":
        formatted_signals.append("⚪ No EMA cross, MACD confirms ongoing uptrend.")
    else:
        formatted_signals.append("⚪ No EMA cross or strong MACD signal.")

    # Add MACD details if present
    if macd_signals and not ema_cross_flag:
        formatted_signals.extend(
            [clean_signal(s) for s in (macd_signals if isinstance(macd_signals, list) else [macd_signals])])

    # Add ADX signals
    if adx_signals:
        formatted_signals.extend(
            [clean_signal(s) for s in (adx_signals if isinstance(adx_signals, list) else [adx_signals])])

    message = "\n  • ".join(formatted_signals)
    log.debug(f"Trend & Momentum signals: {formatted_signals}")
    return message


def generate_support_resistance_message(log, breakout_signal, sr_signals, rsi_signals, wvix_stoch_signals):
    """
    Compiles support/resistance, breakout, and WVIX/Stochastic signals into a single message.

    Args:
        log: Logger instance.
        breakout_signal (list): Breakout messages.
        sr_signals (list): Support/resistance messages.
        rsi_signals (list): RSI messages (ignored, RSI now in wvix_stoch_signals).
        wvix_stoch_signals (list): WVIX/Stochastic messages.

    Returns:
        str: Formatted S/R section message.
    """
    message = "\n📊 *Support & Resistance*"
    all_signals = []

    def clean_signal(signal):
        if isinstance(signal, str):
            return signal.strip().lstrip("  • ").strip()
        return str(signal)

    # Include breakout and S/R signals
    for signal_group in [breakout_signal, sr_signals]:
        if signal_group:
            if isinstance(signal_group, list):
                all_signals.extend(clean_signal(s) for s in signal_group if s)
            else:
                all_signals.append(clean_signal(signal_group))

    # Add WVIX/Stochastic signals (includes RSI)
    if wvix_stoch_signals:
        all_signals.extend(clean_signal(s) for s in wvix_stoch_signals if s)

    if not all_signals:
        message += "  • ⚪ No significant S/R signals detected."
    else:
        message += "\n  • " + "\n  • ".join(all_signals)

    log.debug(f"Support & Resistance signals after cleaning: {all_signals}")
    return message


def detect_wvix_stoch_signals(latest):
    """
    Detects potential market bottoms using Williams VIX Fix, Stochastic Oscillator, and RSI.

    Args:
        latest (pd.Series): Latest data with WVIF, Stochastic, and RSI values.

    Returns:
        tuple: (signals, status)
    """
    signals = []
    status = "HOLD"

    wvix_value = latest.get('WVIF')
    wvix_lower = latest.get('WVIF_BB_LOWER')
    fastk = latest.get('fastk')
    fastd = latest.get('fastd')
    rsi = latest.get('RSI')
    support = latest.get('Support')

    log.debug(f"WVIF: {wvix_value}, WVIF_BB_LOWER: {wvix_lower}, fastk: {fastk}, fastd: {fastd}, RSI: {rsi}")

    if any(pd.isna(x) for x in [wvix_value, wvix_lower, fastk, fastd, rsi]):
        signals.append("⚠️ *WVIX/Stochastic/RSI data unavailable*")
        return signals, status

    # Bottom detection: RSI < 30, Stochastic K & D < 20, WVIX < BB Lower
    rsi_oversold = rsi < 30
    stoch_oversold = fastk < 20 and fastd < 20
    wvix_bottom = wvix_value < wvix_lower

    if rsi_oversold and stoch_oversold and wvix_bottom:
        signals.append(f"🟢 *Bottom Detected!* - RSI {rsi:.2f} < 30, "
                       f"WVIX {wvix_value:.2f} < BB Lower {wvix_lower:.2f}, "
                       f"Stochastic K {fastk:.2f} & D {fastd:.2f} < 20 → Buy at ~{support:.2f}")
        status = "BUY"
    elif rsi_oversold:
        signals.append(f"🟢 RSI {rsi:.2f} < 30 → Oversold, watching for bottom confirmation.")
        signals.append(f"⚪ WVIX {wvix_value:.2f} & Stochastic K {fastk:.2f}, D {fastd:.2f} - No bottom yet.")
    else:
        signals.append(f"⚪ WVIX {wvix_value:.2f} & Stochastic K {fastk:.2f}, D {fastd:.2f} - No bottom signal.")
        signals.append(f"⚪ RSI {rsi:.2f} → Neutral - No strong buy/sell signal.")

    return signals, status
