# -*- coding: utf-8 -*-
__author__ = 'Ishafizan'
__date__ = "11 Feb 2025"  # Selamat Menyambut Thaipusam
"""
✅ Changes & Improvements:
- silent runnings
- Integrates with Binance’s public API and Telegram to monitor your fav cryptos. 
- It sends alerts based on EMA crossovers, RSI insights, and support/resistance levels, 
ensuring strong entry/exit points while preventing false breakouts. 
 🚀
"""
import ccxt
import pandas as pd
import requests
import json
import time
import threading
import websocket
import ssl

# 🔹 Binance API Credentials
api_key = ""
api_secret = ""

# 🔹 Telegram Bot Credentials
TELEGRAM_BOT_TOKEN = ""
TELEGRAM_CHAT_ID = ""

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


# 🔹 Fetch Historical Data and Calculate EMAs, RSI, and Support/Resistance
def get_data(symbol, timeframe):
    bars = exchange.fetch_ohlcv(symbol, timeframe, limit=200)
    df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'volume'])

    # Calculate EMAs
    df['ema_7'] = df['close'].ewm(span=7, adjust=False).mean()
    df['ema_21'] = df['close'].ewm(span=21, adjust=False).mean()
    df['ema_50'] = df['close'].ewm(span=50, adjust=False).mean()
    df['ema_100'] = df['close'].ewm(span=100, adjust=False).mean()
    df['ema_200'] = df['close'].ewm(span=200, adjust=False).mean()

    # Calculate RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))

    # Calculate Support and Resistance Levels
    df['support'] = df['low'].rolling(window=20).min()
    df['resistance'] = df['high'].rolling(window=20).max()

    return df


# THE recipe
# 🔹 Check Buy/Sell Conditions Using EMAs, RSI, and Support/Resistance
def check_signals(df, symbol, timeframe):
    signal_message = None
    last_close = df['close'].iloc[-1]
    last_rsi = df['rsi'].iloc[-1]
    last_support = df['support'].iloc[-1]
    last_resistance = df['resistance'].iloc[-1]

    # 📈 EMA 7 & EMA 21 Crossover (Short-term signals)
    if df['ema_7'].iloc[-2] < df['ema_21'].iloc[-2] and df['ema_7'].iloc[-1] > df['ema_21'].iloc[-1]:
        signal_message = f"📈 *BUY SIGNAL!* {symbol} (Timeframe: {timeframe})\n🔹 Short-term trend turning bullish! (EMA 7 has crossed above EMA 21)\n📊 RSI: {last_rsi:.2f}"

    elif df['ema_7'].iloc[-2] > df['ema_21'].iloc[-2] and df['ema_7'].iloc[-1] < df['ema_21'].iloc[-1]:
        signal_message = f"📉 *SELL SIGNAL!* {symbol} (Timeframe: {timeframe})\n🔹 Short-term trend turning bearish! (EMA 7 has crossed below EMA 21)\n📊 RSI: {last_rsi:.2f}"

    # 📈 EMA 21 & EMA 50 Crossover (Mid-term signals)
    if df['ema_21'].iloc[-2] < df['ema_50'].iloc[-2] and df['ema_21'].iloc[-1] > df['ema_50'].iloc[-1]:
        signal_message = f"🚀 *Bullish Breakout!* {symbol} (Timeframe: {timeframe})\n📈 EMA 21 has crossed above EMA 50! Mid-term bullish momentum.\n📊 RSI: {last_rsi:.2f}"

    elif df['ema_21'].iloc[-2] > df['ema_50'].iloc[-2] and df['ema_21'].iloc[-1] < df['ema_50'].iloc[-1]:
        signal_message = f"⚠️ *Bearish Alert!* {symbol} (Timeframe: {timeframe})\n📉 EMA 21 has crossed below EMA 50! Possible mid-term downtrend.\n📊 RSI: {last_rsi:.2f}"

    # 📈 Golden Cross (EMA 100 & EMA 200 Crossover)
    if df['ema_100'].iloc[-2] < df['ema_200'].iloc[-2] and df['ema_100'].iloc[-1] > df['ema_200'].iloc[-1]:
        signal_message = f"✨ *Golden Cross Detected!* {symbol} (Timeframe: {timeframe})\n🔥 EMA 100 has crossed above EMA 200! Strong long-term bullish confirmation.\n📊 RSI: {last_rsi:.2f}"

    elif df['ema_100'].iloc[-2] > df['ema_200'].iloc[-2] and df['ema_100'].iloc[-1] < df['ema_200'].iloc[-1]:
        signal_message = f"⚠️ *Death Cross Detected!* {symbol} (Timeframe: {timeframe})\n🚨 EMA 100 has crossed below EMA 200! Strong long-term bearish confirmation.\n📊 RSI: {last_rsi:.2f}"

    # 📌 Support and Resistance Alerts
    if last_close <= last_support:
        signal_message += f"\n🟢 *Support Level Reached!* Potential buy zone at {last_support:.2f}"
    elif last_close >= last_resistance:
        signal_message += f"\n🔴 *Resistance Level Reached!* Possible sell area at {last_resistance:.2f}"

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
