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
    df = util_indicators.calculate_indicators(df)
    latest = df.iloc[-1]
    previous = df.iloc[-2]

    ema_signals, ema_status, ema_cross_flag = util_signals.detect_ema_crossovers(latest, previous)
    sr_signals, sr_status = util_signals.detect_support_resistance_sr(latest)
    trend_signals, trend_status = util_signals.detect_trend(df)
    rsi_signals, rsi_status = util_signals.detect_rsi_signals(latest, trend_status)
    breakout_signal, breakout_status = util_signals.detect_breakouts(df)

    all_signals = ema_signals + breakout_signal + sr_signals + rsi_signals + [trend_signals]
    all_signals.append(util_signals.get_market_sentiment(symbol))
    all_signals.append(util_signals.detect_whale_activity(df))

    buy_signals = [s for s in [ema_status, sr_status, rsi_status, breakout_status] if s == "BUY"]
    sell_signals = [s for s in [ema_status, sr_status, rsi_status, breakout_status] if s == "SELL"]

    final_status, final_status_message = util_indicators.determine_final_status(trend_status, buy_signals, sell_signals,
                                                                                latest)
    all_signals.append(f"\n🎯 *DECISION:*\n{final_status_message}")

    # log.info(all_signals)
    log.info(final_status_message)

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
