# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

__author__ = 'Ishafizan'
__date__ = "14 Feb 2025"
__version__ = 7
"""
This program continuously monitors cryptocurrency markets and provides real-time trading signals based on 
multiple technical indicators. It analyzes market trends, detects key trading opportunities,
 and sends alerts via Telegram with insightful analysis.
"""
import time
import settings
from utils import util_log, util_gen, util_indicators, util_signals, util_notify

# Telegram Bot API setup
TELEGRAM_BOT_TOKEN = settings.TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID = settings.TELEGRAM_CHAT_ID

# instantiate logger
log = util_log.logger()


# The main recipe
def detect_signals(df, symbol):
    """
    Identify Buy/Sell/Hold signals based on multiple technical indicators.

    The function analyzes key technical indicators, including:
    - EMA crossovers
    - Support & Resistance levels
    - Trend analysis (using EMA alignment & ADX)
    - RSI overbought/oversold conditions
    - Breakout detection
    - Market sentiment (from Binance funding rates)
    - Whale activity detection

    A final status (BUY, SELL, or HOLD) is determined using a Confirmation-Based Strategy:
    - At least 2 buy/sell signals must align before confirming a trade.
    - Trend strength and volume are factored in to avoid false signals.
    """

    # ✅ Compute all necessary indicators and extract latest price data
    df = util_indicators.calculate_indicators(df)  # Apply indicators to the DataFrame
    latest = df.iloc[-1]  # Latest candle data (most recent)
    previous = df.iloc[-2]  # Previous candle data (for confirming crossovers)

    # ✅ Detect signals from individual technical indicators
    ema_signals, ema_status, ema_cross_flag = util_signals.detect_ema_crossovers(latest, previous)
    sr_signals, sr_status = util_signals.detect_support_resistance_sr(latest)
    trend_signals, trend_status = util_signals.detect_trend(df)
    rsi_signals, rsi_status = util_signals.detect_rsi_signals(latest, trend_status)
    breakout_signal, breakout_status = util_signals.detect_breakouts(df)

    # ✅ Combine all detected signals into a list
    all_signals = ema_signals + breakout_signal + sr_signals + rsi_signals + [trend_signals]

    # ✅ Integrate additional market data for sentiment analysis
    all_signals.append(util_signals.get_market_sentiment(symbol))  # Funding rates-based sentiment
    all_signals.append(util_signals.detect_whale_activity(df))  # Whale accumulation/dumping detection

    # ✅ Count BUY & SELL signals to ensure confirmation-based decision-making
    buy_signals = [status for status in [ema_status, sr_status, rsi_status] if status == "BUY"]
    sell_signals = [status for status in [ema_status, sr_status, rsi_status] if status == "SELL"]

    # ✅ Extract key market conditions
    adx_value = latest.get("ADX", 0)  # ADX value to assess trend strength
    high_volume = latest["volume"] > latest["Volume_MA"]  # Check if volume is above average

    # ✅ Determine the final trading decision using Confirmation-Based Strategy
    if trend_status in ["Strong Uptrend", "Moderate Uptrend"] and len(
            buy_signals) >= 2 and high_volume and adx_value > 25:
        final_status = "BUY"  # Confirmed buy signal in a strong uptrend
    elif trend_status in ["Strong Downtrend", "Moderate Downtrend"] and len(
            sell_signals) >= 2 and high_volume and adx_value > 25:
        final_status = "SELL"  # Confirmed sell signal in a strong downtrend
    elif adx_value < 20:
        final_status = "HOLD"  # Weak trend → Avoid unnecessary trades
    else:
        final_status = "HOLD"  # Default to HOLD if conditions aren't strong enough

    # ✅ Append final decision to signals list
    all_signals.append(f"\n🎯 *DECISION:* {final_status}")

    # ✅ Return the final status, latest closing price, and all compiled signals as a formatted message
    return final_status, latest["close"], "\n".join(all_signals).strip()


def monitor_crypto(symbols):
    """ Main function to monitor cryptos"""
    last_alerts = {}
    while True:
        for symbol in symbols:
            df = util_gen.fetch_binance_data(symbol)
            status, price, signals = detect_signals(df, symbol)

            log.info(f"{symbol} - {status} @ {price:.2f}")
            if signals and last_alerts.get(symbol) != signals:
                formatted_symbol = f"{symbol[:-4]}/{symbol[-4:]}"  # BTCUSDT -> BTC/USDT
                message = f"📊 *Crypto Alert for {formatted_symbol}*\n💰 *Current Price:* {price:.2f} USDT\n\n{signals}\n"
                util_notify.send_alert_sync_with_chart(log, message, df, symbol)
                last_alerts[symbol] = signals

        time.sleep(900)  # Check every 15 minutes


# Main function to monitor cryptos
cryptos = settings.SYMBOLS  # List of cryptos to monitor
monitor_crypto(cryptos)
