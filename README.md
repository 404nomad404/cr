
## 📌 How This Works

-  ChatGPT assisted
- 	Monitors BTC/USDT, XRP/USDT, and WLD/USDT for 1h, 8h, and 1d timeframes. Add your favourites to the symbols list
```
symbols = ['BTC/USDT', 'XRP/USDT', 'WLD/USDT']  # Multi-Crypto Support
```
Whenever you add more cryptocurrencies to the symbols list (e.g., ETH/USDT, SOL/USDT), the WebSocket will auto-subscribe without manual modifications.

- 	Calculates EMA 7, EMA 21, EMA 50, EMA 100, and EMA 200
- 	Detects crossover events for buy/sell signals. The recipe:
      
    >1️⃣ BUY Signal 🚀
    
	>•	EMA 7 > EMA 21 → Short-term uptrend → BUY (BUY when EMA 7 crosses above EMA 21)
    
	>•	EMA 21 > EMA 50 → Mid-term breakout → BUY
    
	>•	Price > EMA 50, 100, 200 → Long-term uptrend → BUY

    >2️⃣ SELL Signal 🔻
    
	>•	EMA 7 < EMA 21 → Short-term weakening → SELL (SELL when EMA 7 crosses below EMA 21)
	
	>•	EMA 21 < EMA 50 → Mid-term breakdown → SELL
	
	>•	Price < EMA 50, 100, 200 → Long-term downtrend → BE CAUTIOUS

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


## 📌 How to Run the Bot

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
 
## 📌 R&D
- Support/Resistance Levels (DONE)
    >Support and resistance (S/R) levels help confirm buy/sell signals by identifying key price areas where the market has historically reversed or consolidated. Adding them to EMA-based strategy can:

    >✅ Increase Trade Accuracy – Prevent false breakouts
    
    >✅ Confirm Buy/Sell Signals – Only trade when price respects key levels
    
    >✅ Identify Strong Entry & Exit Points – Buy near support, sell near resistance
    
    >✅ Detect Trend Reversals – When price breaks through strong S/R levels
    >
<a href="https://ibb.co/Xf2GggtK"><img src="https://i.ibb.co/dsWHqqDV/SCR-20250211-rfkg.png" alt="SCR-20250211-rfkg" border="0"></a>

- RSI for Overbought/Oversold Conditions (DONE-crypto_alert_bot_with_SR_RSI.py)
  >-If RSI is above 50, it suggests bullish momentum—strengthening buy signals.
  >
  >-if RSI is below 50, it suggests bearish momentum—validating sell signals.
<a href="https://ibb.co/5X4VvdfV"><img src="https://i.ibb.co/LDRf6M2f/SCR-20250211-tovs.png" alt="SCR-20250211-tovs" border="0"></a>
- Study RSI, MACD, or volume to reduce fake signals.
- Add backtesting feature:
> 1.	Fetch historical price data (OHLCV - Open, High, Low, Close, Volume).
> 2.	Apply the strategy (e.g., EMA crossovers + RSI confirmation).
> 3.	Simulate trade execution (Buy when criteria are met, sell when exit conditions occur).
> 4.	Calculate performance metrics (profit/loss %, max drawdown, win rate).
