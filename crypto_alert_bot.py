# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals

__author__ = 'Ishafizan'
__date__ = "17 Feb 2025"
__version__ = 14
"""
Crypto Alert Bot: A real-time cryptocurrency market monitoring and trading signal generator.

This program continuously tracks multiple cryptocurrency symbols, leveraging technical indicators and whale activity 
to provide actionable trading signals (BUY, SELL, HOLD). It delivers concise Telegram alerts with detailed analysis 
and price charts, enhancing decision-making for traders.

Key Features:
- Initial and periodic (every 3 hours) full alert broadcasts for all monitored symbols.
- Subsequent alerts triggered only on signal status changes (EMA, RSI, S/R, Breakout, MACD, Stochastic).
- Whale activity detection using Binance volume spikes and Bitcoin-specific Blockchair transaction data.
- Persistent storage of messages, charts, and signal states in Redis with configurable TTL.
- Asynchronous Telegram messaging with 'Read More' option for detailed analysis and charts.
- Comprehensive logging of operations and Redis storage size after each monitoring cycle.
- A final status (BUY, SELL, or HOLD) is determined using a Confirmation-Based Strategy via determine_trade_signal():
    - At least 2 buy/sell signals must align before confirming a trade.
    - Trend strength and volume are factored in to avoid false signals.
"""

import time
import asyncio
import redis
import settings
import io
from utils import util_log, util_gen, util_indicators, util_signals, util_notify, util_chart, util_redis
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CallbackQueryHandler
import pandas as pd

# Telegram Bot API Configuration
TELEGRAM_BOT_TOKEN = settings.TELEGRAM_BOT_TOKEN  # Bot authentication token from Telegram
TELEGRAM_CHAT_ID = settings.TELEGRAM_CHAT_ID  # Target chat ID for group alerts
SEND_CHAT = settings.SEND_CHAT  # Flag to enable/disable Telegram alerts
BOT_USERNAME = settings.BOT_USERNAME  # Bot's Telegram username for private chat links

# Logger Initialization
log = util_log.logger()  # Centralized logging instance for debugging and monitoring

# Redis Connection Setup
redis_client = redis.Redis(
    host=settings.REDIS_HOST,  # Redis server hostname
    port=settings.REDIS_PORT,  # Redis server port
    db=settings.REDIS_DB,  # Redis database index
    decode_responses=False  # Keep responses as bytes for binary data (e.g., charts)
)

# Monitoring Configuration
REFRESH_INTERVAL = settings.REFRESH_INTERVAL  # refresh interval in seconds for full symbol updates


def detect_signals(df, symbol):
    """
    Analyzes market data to generate trading signals based on technical indicators and whale activity.

    Args:
        df (pd.DataFrame): Historical OHLCV data for the given symbol from Binance.
        symbol (str): Cryptocurrency trading pair (e.g., "BTCUSDT").

    Returns:
        tuple: (action, price, alert_message, trade_signals, signal_statuses, df)
    """
    df = util_gen.fetch_binance_data(symbol, interval="1d", limit=20)
    # log.info(f"Raw data for {symbol}: {df[['open', 'high', 'low', 'close', 'volume']].tail(5).to_dict()}")

    if len(df) < 2:
        log.error(f"Insufficient data for {symbol}: {len(df)} rows, need at least 2 for price change")
        latest = df.iloc[-1] if not df.empty else pd.Series({'close': 0, 'volume': 0})
        previous = latest
    else:
        initial_latest = df.iloc[-1].copy()
        previous = df.iloc[-2]
        prev_close = previous["close"]  # Store separately

    # Apply indicators
    df = util_indicators.calculate_indicators(df)
    latest = df.iloc[-1].copy()  # Update with indicators
    latest["Prev_Close"] = prev_close  # Reassign after indicators

    price_change = ((latest["close"] - prev_close) / prev_close) * 100 if prev_close != 0 else 0
    log.info(f"Price change for {symbol}: {price_change:.2f}%, latest={latest['close']:.2f}, prev={prev_close:.2f}")
    log.info(f"Latest before trade signal: {latest[['close', 'Prev_Close', 'ADX', 'volume', 'Volume_MA']].to_dict()}")

    # Detect signals
    ema_signals, ema_status, ema_cross_flag = util_signals.detect_ema_crossovers(log, latest, previous)
    sr_signals, sr_status = util_signals.detect_support_resistance_sr(latest)
    trend_signals, trend_status = util_signals.detect_trend(log, df)
    rsi_signals, rsi_status = util_signals.detect_rsi_signals(latest, trend_status)
    breakout_signal, breakout_status = util_signals.detect_breakouts(df)
    macd_signals, macd_status = util_signals.detect_macd_signal(log, df)
    adx_signals = util_signals.determine_adx_signal(latest, trend_status)
    wvix_stoch_signals, wvix_stoch_status = util_signals.detect_wvix_stoch_signals(latest)

    # Debug adx
    log.info(f"ADX: signals={adx_signals}")
    # Debug MACD
    log.info(f"MACD: signals={macd_signals}, status={macd_status}")

    # Compile analysis sections
    all_signals = [
        util_signals.generate_trend_momentum_message(log, ema_signals, ema_status, ema_cross_flag,
                                                     macd_signals, macd_status, adx_signals, price_change=price_change),
        util_signals.generate_support_resistance_message(log, breakout_signal, sr_signals, rsi_signals,
                                                         wvix_stoch_signals),
        trend_signals,
        util_signals.get_market_sentiment(symbol),
        util_signals.detect_whale_activity(df, symbol)
    ]

    # Determine confirmation states
    ema_confirmation = ema_status in ["BUY", "SELL"]
    rsi_confirmation = rsi_status in ["BUY", "SELL"]
    support_resistance_confirmation = sr_status in ["BUY", "SELL"]
    breakout_confirmation = breakout_status in ["BUY", "SELL"]
    macd_confirmation = macd_status in ["BUY", "SELL"]
    wvix_stoch_confirmation = wvix_stoch_status in ["BUY"]
    log.info(f"Confirmations: EMA={ema_confirmation}, RSI={rsi_confirmation}, SR={support_resistance_confirmation}, "
             f"Breakout={breakout_confirmation}, MACD={macd_confirmation}, WVIX/Stoch={wvix_stoch_confirmation}")

    trade_signal = util_signals.determine_trade_signal(log, ema_confirmation, rsi_confirmation,
                                                       support_resistance_confirmation, breakout_confirmation,
                                                       macd_confirmation, wvix_stoch_confirmation,
                                                       trend_status, latest)

    FINAL_DECISION_MESSAGE = f"\n🎯 *FINAL DECISION:*\n━━━━━━━━━━━━━━\n{trade_signal['message']}"
    if trade_signal["action"] == "BUY" and util_indicators.evaluate_double_down(trade_signal["action"], trend_status,
                                                                                latest):
        FINAL_DECISION_MESSAGE += "\n*Double down* on BUY signal!"
    all_signals.append(FINAL_DECISION_MESSAGE)

    # alert_message = "\n".join(all_signals).strip()
    alert_message = "\n".join(all_signals)

    signal_statuses = {
        "ema_status": ema_status,
        "rsi_status": rsi_status,
        "sr_status": sr_status,
        "breakout_status": breakout_status,
        "macd_status": macd_status,
        "wvix_stoch_status": wvix_stoch_status
    }

    return trade_signal["action"], latest["close"], alert_message, trade_signal, signal_statuses, df


async def monitor_crypto(symbols, stop_event):
    """
    Continuously monitors cryptocurrency markets and sends Telegram alerts based on signal changes.

    Args:
        symbols (list): List of cryptocurrency trading pairs to monitor (e.g., ["BTCUSDT", "ETHUSDT"]).
        stop_event (asyncio.Event): Event to gracefully stop the monitoring loop.

    Behavior:
        - On startup or every 3 hours, sends full alerts for all symbols.
        - Otherwise, sends alerts only when signal statuses change.
        - Stores messages and charts in Redis for retrieval via 'Read More'.
    """
    is_first_run = True  # Flag for initial full alert broadcast
    last_refresh_time = time.time()  # Timestamp of last full refresh

    while not stop_event.is_set():
        current_time = time.time()
        # Trigger full refresh every 3 hours
        if (current_time - last_refresh_time) >= REFRESH_INTERVAL:
            is_first_run = True
            last_refresh_time = current_time
            log.info(
                f"3-hour refresh triggered at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}. Sending alerts for all symbols.")

        for symbol in symbols:
            # Fetch latest market data from Binance
            df = util_gen.fetch_binance_data(symbol)
            # Unpack 6 items including df from detect_signals
            status, price, signals, trade_signals, signal_statuses, df = detect_signals(df, symbol)

            log.info(f"{symbol} - {status} @ {price:.2f}")  # Log current signal status

            # Check previous signal states in Redis
            prev_statuses_key = f"prev_statuses:{symbol}"
            prev_statuses_bytes = redis_client.get(prev_statuses_key)
            prev_statuses = util_redis.deserialize_statuses(prev_statuses_bytes) if prev_statuses_bytes else None

            # Determine if an alert should be sent (first run or status change)
            should_send_alert = is_first_run or (
                    prev_statuses is None or
                    any(signal_statuses[key] != prev_statuses.get(key) for key in signal_statuses)
            )

            if should_send_alert and signals:
                formatted_symbol = f"{symbol[:-4]}/{symbol[-4:]}"
                ttl_minutes = settings.MESSAGE_TTL // 60
                # Short summary message for group chat
                short_message = (
                    f"📊 *Crypto Alert: {formatted_symbol}* → *{status}*\n"
                    f"💰 *Current Price:* {price:.2f} USDT\n\n"
                    f"ℹ️ *Note:* Detailed analysis is available for {ttl_minutes} minutes. Checks are done every {settings.MONITOR_SLEEP // 60} minutes."
                )

                timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                # Full analysis message stored in Redis
                full_message = (
                    f"📊 *Detailed Analysis for {formatted_symbol}*\n({timestamp})\n"
                    f"━━━━━━━━━━━━━━\n"
                    f"💰 *Current Price:* {price:.2f} USDT\n"
                    f"📈 *Status:* {status}\n"
                    f"━━━━━━━━━━━━━━\n\n"
                    f"{signals}"
                )

                if SEND_CHAT:
                    # Generate and store price chart using the updated df
                    chart_image = util_chart.generate_price_chart(df, symbol)
                    if chart_image is None:
                        log.error(f"Failed to generate chart image for {symbol}")
                        continue

                    if isinstance(chart_image, io.BytesIO):
                        chart_image = chart_image.getvalue()

                    # Store message and chart in Redis with TTL
                    message_id = util_redis.generate_message_id(full_message, symbol, time.time())
                    redis_client.setex(f"message:{message_id}", settings.MESSAGE_TTL, full_message.encode('utf-8'))
                    redis_client.setex(f"chart:{message_id}", settings.MESSAGE_TTL, chart_image)
                    log.info(f"Stored full message and chart in Redis for {symbol} with message_id: {message_id}")

                    # Create 'Read More' button for detailed analysis
                    callback_data = f"read_more|{message_id}"
                    read_more_button = InlineKeyboardButton("🔍 Read More", callback_data=callback_data)
                    reply_markup = InlineKeyboardMarkup([[read_more_button]])

                    # Send short alert with chart to Telegram group
                    await util_notify.send_alert_async_with_chart(log, short_message, df, symbol, reply_markup)

                    # Update previous signal statuses in Redis
                    redis_client.set(prev_statuses_key, util_redis.serialize_statuses(signal_statuses))
                    log.info(f"Updated previous signal statuses for {symbol}")

        # Reset first-run flag after full refresh
        if is_first_run:
            is_first_run = False
            log.info("Completed full refresh; resuming normal monitoring.")

        # Log Redis storage size after each cycle
        util_redis.log_redis_size()

        # Sleep until next monitoring cycle or interruption
        try:
            await asyncio.sleep(settings.MONITOR_SLEEP)
        except asyncio.CancelledError:
            log.info("Monitoring loop interrupted, shutting down...")
            break


async def main():
    """
    Main entry point for the bot, initializing Telegram polling and monitoring loop with graceful shutdown.

    Sets up the Telegram bot, connects to Redis, and starts the market monitoring coroutine.
    """
    # Initialize Telegram bot application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.bot_data['redis_client'] = redis_client  # Pass Redis client to bot context
    application.add_handler(CallbackQueryHandler(util_notify.handle_read_more, pattern=r"read_more.*"))

    stop_event = asyncio.Event()  # Event to signal shutdown

    # Start Telegram polling in the background
    log.info("Starting bot polling in the background...")
    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True)
    log.info("Bot started successfully.")

    try:
        # Run the monitoring loop until interrupted
        await monitor_crypto(settings.SYMBOLS, stop_event)
    except KeyboardInterrupt:
        log.info("Received KeyboardInterrupt, shutting down gracefully...")
        stop_event.set()
    finally:
        # Graceful shutdown of Telegram bot and Redis
        log.info("Stopping bot polling...")
        await application.updater.stop()
        await application.stop()
        await application.shutdown()
        log.info("Closing Redis connection...")
        redis_client.close()
        if settings.CLEAR_REDIS_ON_SHUTDOWN:
            log.info("Clearing Redis message storage...")
            util_redis.clear_redis_storage()
        log.info("Application shutdown complete.")


if __name__ == "__main__":
    # Entry point for running the bot
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Program terminated by user.")
