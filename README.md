
# 📊 Crypto Monitoring & Alert Bot 🚀  

## Overview  
This Python script integrates **Binance API** and **Telegram** to monitor cryptocurrency prices, detect trading signals, and send real-time alerts with price charts. 

It helps traders identify **EMA crossovers, RSI signals, and trend strength** to make informed trading decisions.  

## 🔥 Features  

### ✅ **Technical Indicators & Trend Analysis**
- **Exponential Moving Averages (EMA)**  
  - Detects key **EMA crossovers** (7, 21, 50, 100, 200).  
  - Identifies **Golden Cross** (Bullish) and **Death Cross** (Bearish).  
- **Relative Strength Index (RSI)**
  - Alerts when **RSI is oversold (<30) → Buy Signal**.  
  - Alerts when **RSI is overbought (>70) → Sell Signal**.  
- **Average Directional Index (ADX)**
  - Determines if a trend is **strong (ADX > 25)** or **weak/ranging (ADX < 20)**.  
- **Support & Resistance Detection**
  - Detects **price near support (Buy Zone) or resistance (Sell Zone)**.  

### 📡 **Real-Time Alerts via Telegram**
- Sends **clear and meaningful** alerts in **Markdown format**.  
- Prevents **spam** by sending alerts only when conditions change.  
- Includes **price chart images** for better visualization.  

### ⚡ **Reliable Execution & Async Handling**
- Handles **async Telegram alerts** to avoid `asyncio` issues.  
- Uses **error handling** to prevent failures when sending messages.  
- Monitors multiple cryptocurrencies simultaneously.  

## 🚀 How It Works  
1. Fetches **live price data** from Binance API every 15 minutes.  
2. Computes **technical indicators (EMA, RSI, ADX, Support/Resistance)**.  
3. Detects **buy/sell signals** based on indicator crossovers & trend confirmation.  
4. Sends **real-time alerts to Telegram** with price charts.  

## 📂 **Setup Instructions**  
1. Install dependencies:  
   ```bash
   pip install requests pandas numpy matplotlib python-telegram-bot
2.  To create a Telegram bot token
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
4.  Set up Binance API & Telegram Bot in `settings.py`
   ```python
# settings.py

# 🔹 Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = "your_bot_token"  # Replace with your Telegram Bot Token
TELEGRAM_CHAT_ID = "your_chat_id"  # Replace with your Telegram Chat ID

# 🔹 List of Cryptos to Monitor
SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]  # Add more symbols
```
	

5. **Run the BOT**
Once everything is set up, run the script using:

```bash
python crypto_alert_bot.py
```

📌 Example Telegram Alert:

<a href="https://ibb.co/SXvpH4kM"><img src="https://i.ibb.co/wN618FnP/SCR-20250213-tpon.png" alt="SCR-20250213-tpon" border="0"></a>

## 📌 How to Run the backtest script

🚀 Enhancements Added
- ✅ Fetches historical data from Binance
- ✅ Allows selecting any cryptocurrency pair for backtesting
- ✅ Calculates EMA-based BUY/SELL signals
- ✅ Tracks and simulates trading with a $1000 starting balance
- ✅ Plots price, EMA lines, and trade markers (BUY/SELL signals)
- 📊 Outputs
	- ✅ Final Balance
 	- ✅ Total Profit/Loss
  	- ✅ Win Rate (%)
  	- ✅ Trade Log (timestamps & prices)
  	- ✅ Chart with buy/sell signals

##### 1. Install the required Python libraries:
    
```
pip install matplotlib
```
    
##### 2. Run the Script:
```
cd backtest
python backtest_EMA.py
```
##### 3. Enter crypto pair (e.g., BTCUSDT, ETHUSDT, WLDUSDT)

<a href="https://ibb.co/5XNzxsWZ"><img src="https://i.ibb.co/hxPn12R0/SCR-20250212-odeo.png" alt="SCR-20250212-odeo" border="0"></a>

    
## 📌 What I DID NOT do
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
  *Some initial backtesting results:*
  ```
  INITIAL_BALANCE = 1000
  ```
  >

	1. BTC/USDT

  <a href="https://ibb.co/5h9LSHrx"><img src="https://i.ibb.co/PGYgPHcz/Figure-1.png" alt="Figure-1" border="0"></a>
  
  	>🔹 Final Balance: $2583.37
   	>
   	>🔹 Profit/Loss: $1583.37
   	>
   	>🔹 Win Rate: 90.00%

   	2. WLD/USDT
 
   <a href="https://ibb.co/bMg6QJ2P"><img src="https://i.ibb.co/gLMrmVP3/Figure-1.png" alt="Figure-1" border="0"></a>
   
	>🔹 Final Balance: $4958.06
 	>
 	>🔹 Profit/Loss: $3958.06
	>
 	>🔹 Win Rate: 100.00%

	not bad!

  
