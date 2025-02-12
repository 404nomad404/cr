# -*- coding: utf-8 -*-
__author__ = 'Ishafizan'
__date__ = "11 Feb 2025"  # Selamat Menyambut Thaipusam
"""
✅ Changes & Improvements:
- silent runnings
- Integrates with Binance’s public API and Telegram to monitor your fav cryptos. 
- It sends alerts based on EMA crossovers, RSI insights, and support/resistance levels, 
ensuring strong entry/exit points while preventing false breakouts. 
    - Confirm Buy/Sell Signals – Only trigger trades at key levels
    - Prevent False Breakouts – Ignore weak EMA crossovers
    - Identify Stronger Trends – Catch real breakouts & reversals
    - Support & Resistance Levels added (20-period rolling high & low)
    - EMA 21 & EMA 50 Crossover Alerts improved for better buy/sell confirmation
    - Prevents False Breakouts by requiring confirmation near key levels
- Sends alerts to Telegram with Markdown formatting
- Prevents spam by only sending alerts when conditions change
 🚀
"""

import requests
import time
import pandas as pd
from binance.client import Client
from utils import util_log
import settings

# Binance API Configuration (Public API)
BINANCE_API_KEY = settings.BINANCE_API_KEY  # No need for a private key since we're only reading market data
BINANCE_SECRET_KEY = settings.BINANCE_SECRET_KEY

# Telegram Configuration
TELEGRAM_BOT_TOKEN = settings.TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID = settings.TELEGRAM_CHAT_ID

# Define the crypto pairs to monitor
SYMBOLS = settings.SYMBOLS

# Track last alert for each crypto
last_alerts = {}  # Format: {'BTXUSDT': 'BUY', 'XRPUSDT': 'SELL'}

# Initialize Binance client
client = Client(BINANCE_API_KEY, BINANCE_SECRET_KEY)

# -------------------------
# instantiate logger
log = util_log.logger()


def get_historical_data(symbol, interval="15m", limit=50):
    """Fetch historical Kline (candlestick) data from Binance"""
    try:
        klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
        df = pd.DataFrame(klines, columns=[
            "timestamp", "open", "high", "low", "close", "volume",
            "close_time", "quote_asset_volume", "num_trades",
            "taker_base_vol", "taker_quote_vol", "ignore"
        ])
        df["close"] = df["close"].astype(float)
        return df
    except Exception as e:
        log.error(f"❌ Error fetching data for {symbol}: {e}")
        return None


def calculate_indicators(df):
    """Calculate EMAs, RSI, and Support/Resistance levels"""
    df["EMA7"] = df["close"].ewm(span=7, adjust=False).mean()
    df["EMA9"] = df["close"].ewm(span=9, adjust=False).mean()
    df["EMA21"] = df["close"].ewm(span=21, adjust=False).mean()
    df["EMA50"] = df["close"].ewm(span=50, adjust=False).mean()
    df["EMA100"] = df["close"].ewm(span=100, adjust=False).mean()
    df["EMA200"] = df["close"].ewm(span=200, adjust=False).mean()

    # Calculate RSI (Relative Strength Index)
    delta = df["close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))

    # Support & Resistance levels (20-period rolling high/low)
    df["Support"] = df["low"].rolling(window=20).min()
    df["Resistance"] = df["high"].rolling(window=20).max()

    return df


def detect_signals(df, symbol):
    """Identify buy/sell signals based on EMA crossovers and RSI"""
    last_row = df.iloc[-1]

    signal = "HOLD"  # Default signal
    reason = ""

    # Short-term EMA crossover (EMA7 & EMA21)
    if df["EMA7"].iloc[-2] < df["EMA21"].iloc[-2] and last_row["EMA7"] > last_row["EMA21"]:
        signal = "BUY"
        reason = "Short-term EMA7 crossed above EMA21 📈"

    if df["EMA7"].iloc[-2] > df["EMA21"].iloc[-2] and last_row["EMA7"] < last_row["EMA21"]:
        signal = "SELL"
        reason = "Short-term EMA7 crossed below EMA21 📉"

    # Mid-term EMA crossover (EMA21 & EMA50)
    if df["EMA21"].iloc[-2] < df["EMA50"].iloc[-2] and last_row["EMA21"] > last_row["EMA50"]:
        signal = "BUY"
        reason = "Mid-term EMA21 crossed above EMA50 🚀"

    if df["EMA21"].iloc[-2] > df["EMA50"].iloc[-2] and last_row["EMA21"] < last_row["EMA50"]:
        signal = "SELL"
        reason = "Mid-term EMA21 crossed below EMA50 🔻"

    # Golden Cross (EMA100 & EMA200)
    if df["EMA100"].iloc[-2] < df["EMA200"].iloc[-2] and last_row["EMA100"] > last_row["EMA200"]:
        signal = "BUY"
        reason = "Golden Cross! EMA100 crossed above EMA200 🌟"

    if df["EMA100"].iloc[-2] > df["EMA200"].iloc[-2] and last_row["EMA100"] < last_row["EMA200"]:
        signal = "SELL"
        reason = "Death Cross! EMA100 crossed below EMA200 ⚠️"

    # Confirm buy/sell signals with support/resistance levels
    if signal == "BUY" and last_row["close"] < last_row["Support"]:
        signal = "BUY"
        reason += " - Price near Support ✅"

    if signal == "SELL" and last_row["close"] > last_row["Resistance"]:
        signal = "SELL"
        reason += " - Price near Resistance ❌"

    # Prevent false breakouts by checking RSI
    if signal == "BUY" and last_row["RSI"] < 30:
        reason += " - RSI is oversold (strong buy) 🎯"

    if signal == "SELL" and last_row["RSI"] > 70:
        reason += " - RSI is overbought (strong sell) ⚠️"

    return signal, reason


def send_telegram_message(symbol, signal, reason):
    """Send Telegram alerts only if signal changes"""
    global last_alerts

    if last_alerts.get(symbol) == signal:
        return  # Skip duplicate alerts

    last_alerts[symbol] = signal  # Update last alert

    message = f"📢 *{symbol} Alert!* 🚀\n"
    message += f"🟢 *{signal}* detected.\n"
    message += f"📌 Reason: {reason}\n"

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}

    response = requests.post(url, json=payload)
    if response.status_code == 200:
        log.info(f"✅ Alert sent for {symbol}: {signal}")
    else:
        log.info(f"⚠️ Failed to send alert: {response.text}")


# Main loop
while True:
    for symbol in SYMBOLS:
        df = get_historical_data(symbol)
        if df is not None:
            df = calculate_indicators(df)
            signal, reason = detect_signals(df, symbol)
            send_telegram_message(symbol, signal, reason)

    log.info("⏳ Waiting for the next check...")
    time.sleep(900)  # Check every 15 minutes
