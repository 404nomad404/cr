# -*- coding: utf-8 -*-
__author__ = 'Ishafizan'
__date__ = "11 Feb 2025"  # Selamat Menyambut Thaipusam

import ccxt
import pandas as pd
import requests
import json
import time
import threading
import websocket
import ssl

# 🔹 Binance API Credentials
api_key = "YOUR_BINANCE_API_KEY"
api_secret = "YOUR_BINANCE_API_SECRET"

# 🔹 Telegram Bot Credentials
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_TELEGRAM_CHAT_ID"

# 🔹 Initialize Binance Exchange
exchange = ccxt.binance({
    'apiKey': api_key,
    'secret': api_secret,
    'options': {'defaultType': 'spot'},
})

# 🔹 Trading Parameters
symbols = ['BTC/USDT', 'XRP/USDT', 'WLD/USDT']  # Multi-Crypto Support
timeframes = ['1h', '8h', '1d']  # Multiple timeframes


# 🔹 Telegram Notification Function
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': message, 'parse_mode': 'Markdown'}
    requests.post(url, json=payload)


# 🔹 Fetch Historical Data and Calculate EMAs
def get_data(symbol, timeframe):
    bars = exchange.fetch_ohlcv(symbol, timeframe, limit=200)
    df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'volume'])

    # Calculate EMAs
    df['ema_7'] = df['close'].ewm(span=7, adjust=False).mean()
    df['ema_21'] = df['close'].ewm(span=21, adjust=False).mean()
    df['ema_50'] = df['close'].ewm(span=50, adjust=False).mean()
    df['ema_100'] = df['close'].ewm(span=100, adjust=False).mean()
    df['ema_200'] = df['close'].ewm(span=200, adjust=False).mean()

    return df


def check_signals(df, symbol, timeframe):
    signal_message = None
    last_close = df['close'].iloc[-1]

    # 📈 EMA 7 & EMA 21 Crossover (Short-term trend signals)
    if df['ema_7'].iloc[-2] < df['ema_21'].iloc[-2] and df['ema_7'].iloc[-1] > df['ema_21'].iloc[-1]:
        signal_message = f"✅ *BUY SIGNAL!* {symbol} ({timeframe})\n📊 *Short-term bullish trend detected!*\n🔹 EMA 7 crossed above EMA 21 – Momentum is shifting upwards!"

    elif df['ema_7'].iloc[-2] > df['ema_21'].iloc[-2] and df['ema_7'].iloc[-1] < df['ema_21'].iloc[-1]:
        signal_message = f"⚠️ *SELL SIGNAL!* {symbol} ({timeframe})\n📊 *Short-term bearish trend detected!*\n🔻 EMA 7 crossed below EMA 21 – Momentum is weakening."

    # 🚀 EMA 21 & EMA 50 Crossover (Mid-term trend signals)
    if df['ema_21'].iloc[-2] < df['ema_50'].iloc[-2] and df['ema_21'].iloc[-1] > df['ema_50'].iloc[-1]:
        signal_message = f"✅ *BUY SIGNAL!* {symbol} ({timeframe})\n🚀 *Mid-term bullish breakout!*\n🔹 EMA 21 crossed above EMA 50 – Stronger bullish momentum building!"

    elif df['ema_21'].iloc[-2] > df['ema_50'].iloc[-2] and df['ema_21'].iloc[-1] < df['ema_50'].iloc[-1]:
        signal_message = f"⚠️ *SELL SIGNAL!* {symbol} ({timeframe})\n📉 *Mid-term bearish reversal detected!*\n🔻 EMA 21 crossed below EMA 50 – Market could be turning bearish."

    # 🔥 EMA 50, 100, and 200 Crossovers (Long-term trend confirmations)
    if last_close > df['ema_50'].iloc[-1] and last_close < df['ema_50'].iloc[-2]:
        signal_message = f"⚠️ *Warning!* {symbol} ({timeframe})\n📉 *Price just dropped below EMA 50!* Possible short-term downtrend ahead."
    elif last_close < df['ema_50'].iloc[-1] and last_close > df['ema_50'].iloc[-2]:
        signal_message = f"✅ *Bullish Signal!* {symbol} ({timeframe})\n📈 *Price broke above EMA 50!* Buyers are gaining control."

    if last_close > df['ema_100'].iloc[-1] and last_close < df['ema_100'].iloc[-2]:
        signal_message = f"⚠️ *Caution!* {symbol} ({timeframe})\n📉 *Price dropped below EMA 100!* Medium-term bearish pressure increasing."
    elif last_close < df['ema_100'].iloc[-1] and last_close > df['ema_100'].iloc[-2]:
        signal_message = f"🔥 *Momentum Gaining!* {symbol} ({timeframe})\n📈 *Price broke above EMA 100!* Strong bullish sentiment."

    if last_close > df['ema_200'].iloc[-1] and last_close < df['ema_200'].iloc[-2]:
        signal_message = f"🚨 *Major Warning!* {symbol} ({timeframe})\n⚠️ *Price dropped below EMA 200!* Long-term bearish trend confirmed!"
    elif last_close < df['ema_200'].iloc[-1] and last_close > df['ema_200'].iloc[-2]:
        signal_message = f"🚀 *STRONG BULLISH SIGNAL!* {symbol} ({timeframe})\n🔥 *Price broke above EMA 200!* Long-term uptrend confirmed!"

    return signal_message


# 🔹 WebSocket Updates
def on_message(ws, message):
    try:
        data = json.loads(message)
        if 's' in data and 'p' in data:
            symbol = data['s']
            price = float(data['p'])
            print(f"📊 Real-time {symbol} Price: {price}")
        else:
            print("⚠️ Received non-trade message:", data)
    except Exception as e:
        print(f"⚠️ WebSocket Error: {e}")


# Update: Automatically subscribes to all cryptos in the symbols list
def on_open(ws):
    print("✅ WebSocket connected.")
    subscription_list = [symbol.lower().replace("/", "") + "@trade" for symbol in symbols]
    ws.send(json.dumps({
        "method": "SUBSCRIBE",
        "params": subscription_list,
        "id": 1
    }))


def on_error(ws, error):
    print(f"⚠️ WebSocket Error: {error}")


def on_close(ws, close_status_code, close_msg):
    print("❌ WebSocket closed. Reconnecting...")
    start_websocket()


def start_websocket():
    ws = websocket.WebSocketApp(
        "wss://stream.binance.com:9443/ws",
        on_message=on_message,
        on_open=on_open,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})


# 🔹 Main Trading Loop
def trading_loop():
    while True:
        try:
            for symbol in symbols:
                for timeframe in timeframes:
                    df = get_data(symbol, timeframe)
                    signal = check_signals(df, symbol, timeframe)
                    if signal:
                        print(signal)
                        send_telegram_message(signal)
            time.sleep(300)
        except Exception as e:
            print(f"⚠️ Error: {e}")
            time.sleep(60)


# 🔹 Start Trading Bot
if __name__ == "__main__":
    print("🚀 Starting Binance Trading Bot for %s..." % symbols)
    ws_thread = threading.Thread(target=start_websocket)
    ws_thread.daemon = True
    ws_thread.start()
    trading_loop()
