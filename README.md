
# 📊 Crypto Monitoring & Alert Bot 🚀  

## Overview  
This Python script integrates **Binance API** and **Telegram** to monitor cryptocurrency prices, detect trading signals, and send real-time alerts with price charts. 

It helps traders identify **EMA crossovers, RSI signals, and trend strength** to make informed trading decisions.  

## 🔥 Features  


### ✅ **Real-time Market Monitoring**
- Fetches historical price data from Binance every 15 minutes.
- Supports multiple crypto pairs (configurable in settings.SYMBOLS).

### ✅ **Technical Indicators & Trend Analysis**
- **Exponential Moving Averages (EMA)**  
  - Detects key **EMA crossovers** (7, 21, 50, 100, 200).  
  - Identifies **Golden Cross** (Bullish) and **Death Cross** (Bearish).
    
  - #### 🔥 How This Improves Decision Making

| **EMA Crossover**                    | **BUY Alert**                    | **SELL Alert**                    | **Why It Matters**                    |
|---------------------------------------|----------------------------------|----------------------------------|--------------------------------------|
| **EMA100/EMA200** (Golden/Death Cross) | *EMA100 crossed above EMA200*   | *EMA100 crossed below EMA200*   | **Strong long-term trend change**  |
| **EMA50/EMA100**                      | *EMA50 crossed above EMA100*    | *EMA50 crossed below EMA100*    | **Medium-term trend confirmation** |
| **EMA21/EMA50**                        | *EMA21 crossed above EMA50*     | *EMA21 crossed below EMA50*     | **Early medium-term trend shift**  |
| **EMA7/EMA21**                         | *EMA7 crossed above EMA21*      | *EMA7 crossed below EMA21*      | **Short-term momentum change**     |


- **Relative Strength Index (RSI)**
  - RSI-based alerts for momentum-based trades
  - Alerts when **RSI is oversold (<30) → Buy Signal**.  
  - Alerts when **RSI is overbought (>70) → Sell Signal**.  
- **Average Directional Index (ADX)**
  - Implements ADX (Average Directional Index) to confirm trend strength.
  - Adding trend detection can help you:
    
	>✅ Avoid bad trades by filtering weak signals.
 	>
	>✅ Confirm strong buy/sell signals based on trend strength.
  	>
	>✅ Hold your position instead of reacting to every small price movement.
  - Identifies Strong Uptrend, Strong Downtrend, or Weak/Ranging Markets using EMA alignment and ADX strength.
  - Determines if a trend is **strong (ADX > 25)** or **weak/ranging (ADX < 20)**.
  - Prevents false signals by avoiding trades in weak-trend conditions.
- **Support & Resistance Detection**
  - Detects **price near support (Buy Zone) or resistance (Sell Zone)**.
    
  <a href="https://ibb.co/Xf2GggtK"><img src="https://i.ibb.co/dsWHqqDV/SCR-20250211-rfkg.png" alt="SCR-20250211-rfkg" border="0"></a>

 
### 📡 **Automated Real-Time Alerts via Telegram**
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
5. The system ensures alerts are only sent when new conditions appear to prevent redundant notifications.

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
4.  Set up Telegram Bot in `settings.py`
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

	✅ Sends a message with price trend alerts.

	✅ Attaches a small trend chart showing the last 50 candles.

	✅ Helps visualize price movement before making decisions.

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

Examples:    
  
   1. BTC/USDT

  <a href="https://ibb.co/5h9LSHrx"><img src="https://i.ibb.co/PGYgPHcz/Figure-1.png" alt="Figure-1" border="0"></a>
  
  	🔹 Final Balance: $2583.37
   	
   	🔹 Profit/Loss: $1583.37
   	
   	🔹 Win Rate: 90.00%

   2. WLD/USDT
 
   <a href="https://ibb.co/bMg6QJ2P"><img src="https://i.ibb.co/gLMrmVP3/Figure-1.png" alt="Figure-1" border="0"></a>
   
	🔹 Final Balance: $4958.06
 	
 	🔹 Profit/Loss: $3958.06
	
 	🔹 Win Rate: 100.00%

   not bad!
    
## 📌 What I DID NOT do
- Add automatic order execution to buy/sell directly on Binance. 
- Can do if there's a safe sandbox i can play around. Do it manually-lah for now, jgn malas 😂

## 📌 FUTURE BOT IDEAS

1. **Trade Confidence & Signal Strength**

	✅ Signal Strength Meter – Assign confidence levels to signals (e.g., weak/medium/strong) based on multiple confirmations.

	✅ Trend Score – Score from 1 to 100 based on EMAs, RSI, and momentum. Helps gauge bullish/bearish strength.


2. **Additional Market Insights**

	✅ Volume Analysis – Identify spikes in buying/selling volume to confirm trend strength.

	✅ Volatility Indicator – Show if the market is trending or ranging to avoid fakeouts.

	✅ MACD Indicator – Add another confirmation layer to trend shifts.


3. **Improved Alerts & Decision Support**

	✅ Risk/Reward Estimation – Suggest optimal entry price, stop-loss, and take-profit levels.

	✅ Support/Resistance Breakout Detection – Alert when price breaks past key levels instead of just touching them.

	✅ Whale Activity Alert – Detect unusual buy/sell volume spikes indicating large trader moves.

	✅ Market Sentiment Check – Integrate data from sources like Binance funding rates to gauge trader sentiment.



4. User Customization

	✅ Adjustable Thresholds – Allow you to tweak RSI, EMA crossovers, and risk levels dynamically.

	✅ Multi-Crypto Filtering – Rank and sort monitored cryptos based on trend strength.
 
  
  


  
