
## 📌 How This Works

-  ChatGPT assisted
- 	Monitors BTC/USDT, XRP/USDT, and WLD/USDT for 1h, 8h, and 1d timeframes. Add your favourites to the symbols list
```
symbols = ['BTC/USDT', 'XRP/USDT', 'WLD/USDT']  # Multi-Crypto Support
```
- 	Calculates EMA 7, EMA 21, EMA 50, EMA 100, and EMA 200
- 	Detects crossover events for buy/sell signals
      >📈 BUY when EMA 7 crosses above EMA 21
      >
      >📉 SELL when EMA 7 crosses below EMA 21
      >
      >⚠️ Alerts when price crosses EMA 50, 100, or 200
      >
      >✅ “Strong Bullish Signal! 🚀 BTC has broken above EMA 200 on the 1D chart!”
      >
      >“Warning! BTC has dropped below EMA 100 on the 8H chart! Possible downtrend!”
-   Sends alerts to Telegram
      >Uses Markdown in Telegram for better readability
-   Uses Binance WebSockets for real-time updates
-   Runs continuously, checking the market every 5 minutes

```
symbols = ['BTC/USDT', 'XRP/USDT', 'WLD/USDT']  # Multi-Crypto Support
```

## 📌 How to Run the Bot

##### 1. Replace API Keys:

- 	Add your Binance API keys (api_key, api_secret)
- 	Add your Telegram Bot Token and Chat ID

##### 2. Install Dependencies:
```
pip install ccxt requests websocket-client pandas numpy python-telegram-bot
```
##### 3. Run the Script:
```
python crypto_alert_bot.py
```

## 📌 What I DID NOT DO
- Add automatic order execution to buy/sell directly on Binance. 
- Haha can do if there's a safe sandbox i can play around. Do it manually-lah, jgn malas 😂
 
