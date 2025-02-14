# -*- coding: utf-8 -*-
__author__ = 'Ishafizan'
__date__ = "13 Feb 2025"
"""
This Python script integrates Binance’s public API with Telegram to monitor cryptocurrency price movements 
and send meaningful alerts. It utilizes technical indicators such as EMA crossovers, RSI levels, 
ADX trend strength, and support/resistance detection to identify potential trade opportunities 
while reducing false signals.
"""
import requests
import time
import pandas as pd
import numpy as np
import asyncio
import telegram
import logging
import settings
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io

# Telegram Bot API setup
TELEGRAM_BOT_TOKEN = settings.TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID = settings.TELEGRAM_CHAT_ID
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s : %(levelname)s : %(message)s")

# Binance API URL
BINANCE_URL = "https://api.binance.com/api/v3/klines"


# Fetch historical data
def fetch_binance_data(symbol, interval="1d", limit=500):
    url = f"{BINANCE_URL}?symbol={symbol}&interval={interval}&limit={limit}"
    response = requests.get(url)
    data = response.json()
    df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close", "volume", "close_time",
                                     "quote_asset_volume", "trades", "taker_base_volume", "taker_quote_volume",
                                     "ignore"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df["close"] = df["close"].astype(float)
    df.set_index("timestamp", inplace=True)
    return df[["close"]]


# Calculate EMAs
def calculate_ema(df, span):
    return df["close"].ewm(span=span, adjust=False).mean()


# Calculate RSI
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


# Calculate ADX for trend strength
def calculate_adx(df, period=14):
    df["high-low"] = df["close"].diff().abs()
    df["+DM"] = df["close"].diff().where(df["close"].diff() > 0, 0)
    df["-DM"] = -df["close"].diff().where(df["close"].diff() < 0, 0)
    df["+DI"] = (df["+DM"].rolling(window=period).mean() / df["high-low"].rolling(window=period).mean()) * 100
    df["-DI"] = (df["-DM"].rolling(window=period).mean() / df["high-low"].rolling(window=period).mean()) * 100
    df["DX"] = abs(df["+DI"] - df["-DI"]) / (df["+DI"] + df["-DI"]) * 100
    df["ADX"] = df["DX"].rolling(window=period).mean()
    return df["ADX"]


# Detect trend based on EMA alignment and ADX strength
def detect_trend(df):
    df["EMA50"] = calculate_ema(df, 50)
    df["EMA100"] = calculate_ema(df, 100)
    df["EMA200"] = calculate_ema(df, 200)
    df["ADX"] = calculate_adx(df)

    latest = df.iloc[-1]
    trend = "Neutral"

    # EMA Alignment:
    if latest["EMA50"] > latest["EMA100"] > latest["EMA200"] and latest["ADX"] > 25:
        trend = "Strong Uptrend"  # recent price movements are trending upward and confirming bullish momentum
    elif latest["EMA50"] < latest["EMA100"] < latest["EMA200"] and latest["ADX"] > 25:
        trend = "Strong Downtrend"
    # ADX Strength
    elif latest["ADX"] < 20:  # Trends are weak, and trades should be taken cautiously.
        trend = "Weak Trend / Ranging"

    return trend


# Generate price chart with EMA crossovers
def generate_price_chart(df, symbol):
    plt.figure(figsize=(8, 4))  # Increase figure size for better visibility

    # Plot price and EMAs
    plt.plot(df.index[-100:], df["close"].tail(100), label="Price", color="blue", linewidth=2)
    plt.plot(df.index[-100:], df["EMA21"].tail(100), label="EMA21", color="green", linestyle="dashed")
    plt.plot(df.index[-100:], df["EMA50"].tail(100), label="EMA50", color="orange", linestyle="dashed")
    plt.plot(df.index[-100:], df["EMA100"].tail(100), label="EMA100", color="red", linestyle="dashed")
    plt.plot(df.index[-100:], df["EMA200"].tail(100), label="EMA200", color="purple", linestyle="dashed")

    plt.title(f"{symbol} Price & EMA Crossovers")
    plt.xlabel("Time")
    plt.ylabel("Price (USDT)")
    plt.grid(True)
    plt.legend()

    # Format x-axis for better readability
    plt.xticks(rotation=45)  # Rotate labels
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))  # Format as "MM-DD HH:MM"
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())  # Auto-adjust ticks

    # Save chart to a BytesIO object
    img = io.BytesIO()
    plt.savefig(img, format="png", bbox_inches="tight", dpi=200)  # Increase DPI for better quality
    img.seek(0)
    plt.close()
    return img


# Identify Buy/Sell Signals
def detect_signals(df):
    df["EMA7"] = calculate_ema(df, 7)
    df["EMA21"] = calculate_ema(df, 21)
    df["EMA50"] = calculate_ema(df, 50)
    df["EMA100"] = calculate_ema(df, 100)
    df["EMA200"] = calculate_ema(df, 200)
    df["RSI"] = calculate_rsi(df["close"])
    df["Support"] = df["close"].rolling(20).min()
    df["Resistance"] = df["close"].rolling(20).max()

    trend = detect_trend(df)
    latest = df.iloc[-1]
    previous = df.iloc[-2]
    status = "HOLD"
    ema_cross_flag = False
    signals = []

    # EMA100 & EMA200 (Golden/Death Cross)
    if latest["EMA100"] > latest["EMA200"] and previous["EMA100"] <= previous["EMA200"]:
        ema_cross_flag = True
        signals.append(
            "✅ *EMA100 crossed above EMA200* - Buy (Golden Cross)\n🔥 This is a long-term bullish signal, suggesting strong momentum!")
        status = "BUY"
    if latest["EMA100"] < latest["EMA200"] and previous["EMA100"] >= previous["EMA200"]:
        ema_cross_flag = True
        signals.append("❌ *EMA100 crossed below EMA200* - Sell (Death Cross)\n	🚨 A bearish trend is forming")
        status = "SELL"

    # EMA50 & EMA100
    if latest["EMA50"] > latest["EMA100"] and previous["EMA50"] <= previous["EMA100"]:
        ema_cross_flag = True
        signals.append("✅ *EMA50 crossed above EMA100* - Buy")
        status = "BUY"
    if latest["EMA50"] < latest["EMA100"] and previous["EMA50"] >= previous["EMA100"]:
        ema_cross_flag = True
        signals.append("❌ *EMA50 crossed below EMA100* - Sell")
        status = "SELL"

    # EMA21 & EMA50
    if latest["EMA21"] > latest["EMA50"] and previous["EMA21"] <= previous["EMA50"]:
        ema_cross_flag = True
        signals.append("✅ *EMA21 crossed above EMA50* - Buy")
        status = "BUY"
    if latest["EMA21"] < latest["EMA50"] and previous["EMA21"] >= previous["EMA50"]:
        ema_cross_flag = True
        signals.append("❌ *EMA21 crossed below EMA50* - Sell")
        status = "SELL"

    # EMA7 & EMA21
    if latest["EMA7"] > latest["EMA21"] and previous["EMA7"] <= previous["EMA21"]:
        ema_cross_flag = True
        signals.append("✅ *EMA7 crossed above EMA21* - Short-term Buy Signal")
        status = "BUY"
    if latest["EMA7"] < latest["EMA21"] and previous["EMA7"] >= previous["EMA21"]:
        ema_cross_flag = True
        signals.append("❌ *EMA7 crossed below EMA21* - Short-term Sell Signal")
        status = "SELL"

    # Price Near Support/Resistance
    if latest["close"] <= latest["Support"] * 1.02:
        signals.append("🔵 *Price Near Support* - Buying Opportunity")
        status = "BUY"
    if latest["close"] >= latest["Resistance"] * 0.98:
        signals.append("🔴 *Price Near Resistance* → Potential selling pressure ahead!")
        status = "SELL"

    # RSI Conditions
    if latest["RSI"] < 30:
        signals.append(
            "🟢 *RSI < 30 → Oversold* - Strong Buy\n📢 *Buyers could step in soon, but wait for confirmation!*")
        status = "BUY"
    if latest["RSI"] > 70:
        signals.append("🔴 *RSI > 70 → Overbought* - Strong Sell")
        status = "SELL"

    # Trend detection
    if trend == "Strong Uptrend":
        signals.append("📈 *ADX > 25 (Strong Trend) Uptrend Confirmed*")
    elif trend == "Strong Downtrend":
        signals.append("📉 *Downtrend Confirmed - Favoring Sells*")
    elif trend == "Weak Trend / Ranging":
        signals.append(
            "⚠️ *ADX<20 - No Clear Trend - Market Ranging - Trade with Caution*\n⚠️ Ignore the buy signal")

    # Final bias
    if trend == "Strong Uptrend" and latest["RSI"] < 30 and status == "BUY" and ema_cross_flag is True:
        signals.append("📉 *Overall bias: 🔥 CONFIRM BUY! 🔥*")
    elif trend == "Strong Uptrend" and latest["RSI"] < 30 and status == "BUY":  # EMAs didn't cross
        signals.append("📉 *Overall bias: 🔥 BUY 🥶*")
    elif trend == "Strong Downtrend" and latest["RSI"] > 70 and status == "SELL" and ema_cross_flag is True:
        signals.append("📉 *Overall bias: ❌ CONFIRM SELL! 🔥*")
    elif trend == "Strong Downtrend" and latest["RSI"] > 70 and status == "SELL":  # EMAs didn't cross
        signals.append("📉 *Overall bias: ❌ SELL 🔥🥶*")
    else:
        signals.append("📉 *Overall bias: 🥶 %s, better to wait for other confirmations*" % status)

    return status, latest["close"], "\n".join(signals).strip()


# Send Telegram Alert (Fix for asyncio issues)
async def send_telegram_alert2(message):
    try:
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Failed to send Telegram message: {e}")


# Send Telegram alert with chart
async def send_telegram_alert_with_chart(message, df, symbol):
    try:
        img = generate_price_chart(df, symbol)
        await bot.send_photo(chat_id=TELEGRAM_CHAT_ID, photo=img, caption=message, parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Failed to send Telegram message with chart: {e}")


def send_alert_sync_with_chart(message, df, symbol):
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    loop.run_until_complete(send_telegram_alert_with_chart(message, df, symbol))


# Main function to monitor cryptos
def monitor_crypto(symbols):
    last_alerts = {}
    while True:
        for symbol in symbols:
            df = fetch_binance_data(symbol)
            status, price, signals = detect_signals(df)
            logging.info(f"{symbol} - {status} @ {price:.2f}")

            if signals and last_alerts.get(symbol) != signals:
                # message = f"📊 *Crypto Alert for {symbol}* \n{signals}\n💰 *Current Price:* {price:.2f} USDT"
                formatted_symbol = f"{symbol[:-4]}/{symbol[-4:]}"  # BTCUSDT -> BTC/USDT
                message = f"📊 *Crypto Alert for {formatted_symbol}*\n💰 *Current Price:* {price:.2f} USDT\n{signals}"
                # send_alert_sync(message)
                send_alert_sync_with_chart(message, df, symbol)
                last_alerts[symbol] = signals

        time.sleep(900)  # Check every 15 minutes


# Main function to monitor cryptos
# List of cryptos to monitor
cryptos = settings.SYMBOLS
monitor_crypto(cryptos)
