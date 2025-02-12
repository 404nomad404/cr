
## 📌 How This Works

- ChatGPT assisted
- It sends alerts based on EMA crossovers, RSI insights, and support/resistance levels, 
ensuring strong entry/exit points while preventing false breakouts.
-   Sends alerts to Telegram
    - Prevents spam by only sending alerts when conditions change  
    - Uses Markdown in Telegram for better readability

      Telegram message examples:
      ><a href="https://ibb.co/ZpZW6k70"><img src="https://i.ibb.co/Kp1Fj3SJ/SCR-20250212-mjbj.png" alt="SCR-20250212-mjbj" border="0"></a>
-   Uses Binance WebSockets for real-time updates. Its public API allows users to access market data, such as price and trading volume, WITHOUT any cost
-   Runs continuously, checking the market every 15 minutes 

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
pip install requests websocket-client pandas numpy python-telegram-bot python-binance
```


## 📌 How to Run the Bots

##### 1. Replace API Keys in settings.py:

- 	Add your Binance API keys (api_key, api_secret)
- 	Add your Telegram Bot Token and Chat ID
```
# ----------------------------------------------
# Binance API Configuration (Public API)
BINANCE_API_KEY = ""  
BINANCE_SECRET_KEY = ""
# ----------------------------------------------
# Telegram Configuration
TELEGRAM_BOT_TOKEN = ""
TELEGRAM_CHAT_ID = "1234567899"  # example
```
##### 2. Replace crypto-pair in settings.py:
```
SYMBOLS = ["BTCUSDT", "XRPUSDT", "WLDUSDT", "ETHUSDT"]
```

##### 3. Run the Script:
```
python crypto_alert_bot.py
```
<a href="https://ibb.co/96qHnMM"><img src="https://i.ibb.co/Dh7f4qq/SCR-20250212-mfwo.png" alt="SCR-20250212-mfwo" border="0"></a>

That's it!

## 📌 What I DID NOT DO
- Add automatic order execution to buy/sell directly on Binance. 
- Can do if there's a safe sandbox i can play around. Do it manually-lah for now, jgn malas 😂
 
## 📌 R&D
- Support/Resistance Levels (DONE)
    >Support and resistance (S/R) levels help confirm buy/sell signals by identifying key price areas where the market has historically reversed or consolidated. Adding them to EMA-based strategy can:

    >✅ Increase Trade Accuracy – Prevent false breakouts
    
    >✅ Confirm Buy/Sell Signals – Only trade when price respects key levels
    
    >✅ Identify Strong Entry & Exit Points – Buy near support, sell near resistance
    
    >✅ Detect Trend Reversals – When price breaks through strong S/R levels
    ><a href="https://ibb.co/Xf2GggtK"><img src="https://i.ibb.co/dsWHqqDV/SCR-20250211-rfkg.png" alt="SCR-20250211-rfkg" border="0"></a>

- RSI for Overbought/Oversold Conditions (DONE)
  >-If RSI is above 50, it suggests bullish momentum—strengthening buy signals.
  >
  >-if RSI is below 50, it suggests bearish momentum—validating sell signals.
  >
  
  
- backtest (In progress)
    - Loads historical Binance data
    - Applies EMA crossovers, Support/Resistance, RSI rules
    - Simulate buy/sell trades as per recipe in bot
    - Calculates balance, total profit/loss, win rate, and performance metrics
    - Trade Log (timestamps & prices)
    - Graph with buy/sell signals (matplotlib)
    - Tune recipe with chatgpt
  

  *Some initial backtesting results:*
  ```
  INITIAL_BALANCE = 1000
  INTERVAL = "1d"  # Backtest on 1d candles
  LIMIT = 1000  # Number of historical candles to fetch
  ```
  >

	1. BTC/USDT

  <a href="https://ibb.co/9HBwFrcF"><img src="https://i.ibb.co/yFKhwQdw/Figure-1.png" alt="Figure-1" border="0"></a>
  
  	>🔹 Final Balance: $1941.38
   	>
   	>🔹 Profit/Loss: $941.38
   	>
   	>🔹 Win Rate: 39.13%

   	2. WLD/USDT
 
   <a href="https://ibb.co/hF3JsHyz"><img src="https://i.ibb.co/9HQkn2N5/Figure-2.png" alt="Figure-2" border="0"></a>
   
	>🔹 Final Balance: $4363.90
 	>
 	>🔹 Profit/Loss: $3363.90
	>
 	>🔹 Win Rate: 100.00%

	not bad!

  
