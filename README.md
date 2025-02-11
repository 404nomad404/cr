
## 📌 How This Works

-  ChatGPT assisted
- 	Monitors BTC/USDT, XRP/USDT, and WLD/USDT for 1h, 8h, and 1d timeframes. Add your favourites to the symbols list
```
symbols = ['BTC/USDT', 'XRP/USDT', 'WLD/USDT']  # Multi-Crypto Support
```
Whenever you add more cryptocurrencies to the symbols list (e.g., ETH/USDT, SOL/USDT), the WebSocket will auto-subscribe without manual modifications.

- 	Calculates EMA 7, EMA 21, EMA 50, EMA 100, and EMA 200
- 	Detects crossover events for buy/sell signals
      >📈 BUY when EMA 7 crosses above EMA 21
      >
      >📉 SELL when EMA 7 crosses below EMA 21
      >
      >📈 BUY when EMA 21 crosses above EMA 50
      >
      >📉 SELL when EMA 21 crosses below EMA 50
      >
      >⚠️ Alerts when price crosses EMA 50, 100, or 200
      > ... and more.

      Examples:
      >✅ “*STRONG BULLISH SIGNAL!* 🚀 {symbol} *Price broke above EMA 200!* Long-term uptrend confirmed!”
      >
      
-   Sends alerts to Telegram
      >Uses Markdown in Telegram for better readability
-   Uses Binance WebSockets for real-time updates. Its public API allows users to access market data, such as price and trading volume, WITHOUT any cost
-   Runs continuously, checking the market every 5 minutes

## 📌 Requirements

1.	Create a Binance API Key https://www.binance.com/en/my/settings/api-management
2.  To create a bot token 
    - Open the Telegram app
    - Search for "@BotFather"
    - Start a chat with BotFather
    - Type /newbot
    - Follow the instructions to name and username your bot
    - BotFather will send you a unique API token
3. To create a chat ID 
    - Create a new chat group
    - Add your bot to the group
    - Go to Telegram Web and log in to your account
    - Select the group chat
    - The chat ID (numbers/digits) is in the URL in the address bar
4. Install the required Python libraries:
```
pip install ccxt requests websocket-client pandas numpy python-telegram-bot
```


## 📌 How to Run the crypto_alert_bot.py

##### 1. Replace API Keys:

- 	Add your Binance API keys (api_key, api_secret)
- 	Add your Telegram Bot Token and Chat ID

##### 2. Run the Script:
```
python crypto_alert_bot.py
```

That's it!

## 📌 What I DID NOT DO
- Add automatic order execution to buy/sell directly on Binance. 
- Can do if there's a safe sandbox i can play around. Do it manually-lah for now, jgn malas 😂
 
