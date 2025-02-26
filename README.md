
# 📊 Crypto Monitoring & Alert Bot 🚀  

## Overview  
Welcome to the **Crypto Alert Bot**, a powerful Python-based tool designed to monitor cryptocurrency markets in real-time and deliver actionable trading signals directly to your Telegram chat. Whether you're a seasoned trader or just starting out, this bot leverages advanced technical indicators and whale activity detection to help you stay ahead of market trends. Built with flexibility and reliability in mind, it integrates seamlessly with Binance for market data, Redis for persistent storage, and Telegram for instant notifications.

Perfect for enthusiasts and developers alike, this bot combines robust signal analysis with an intuitive alert system—complete with price charts and detailed breakdowns. 

Ready to take your crypto trading to the next level? Let’s dive in!

## 🔥 Features  


### ✅ **Real-time Market Monitoring**
- Fetches historical price data from Binance every 15 minutes.
- Supports multiple crypto pairs (configurable in settings.SYMBOLS).

### ✅ **Technical Indicators & Trend Analysis**
1. **Exponential Moving Averages (EMA)**  
  - Detects key **EMA crossovers** (7, 21, 50, 100, 200) to identify bullish & bearish moving average crossovers
  - Identifies **Golden Cross** (Bullish) and **Death Cross** (Bearish).
  - Filters EMA cross signals with RSI (trend strength) and ADX (momentum)
    
  - #### 🔥 How This Improves Decision Making

| **EMA Crossover**                    | **BUY Alert**                    | **SELL Alert**                    | **Why It Matters**                    |
|---------------------------------------|----------------------------------|----------------------------------|--------------------------------------|
| **EMA100/EMA200** (Golden/Death Cross) | *EMA100 crossed above EMA200*   | *EMA100 crossed below EMA200*   | **Strong long-term trend change**  |
| **EMA50/EMA100**                      | *EMA50 crossed above EMA100*    | *EMA50 crossed below EMA100*    | **Medium-term trend confirmation** |
| **EMA21/EMA50**                        | *EMA21 crossed above EMA50*     | *EMA21 crossed below EMA50*     | **Early medium-term trend shift**  |
| **EMA7/EMA21**                         | *EMA7 crossed above EMA21*      | *EMA7 crossed below EMA21*      | **Short-term momentum change**     |


2. **Relative Strength Index (RSI)**
  - RSI-based alerts for momentum-based trades
  - Alerts when **RSI is oversold (<30) → Buy Signal**.  
  - Alerts when **RSI is overbought (>70) → Sell Signal**.
  - Adjusts RSI buy/sell levels dynamically based on trend conditions
    
3. **Average Directional Index (ADX)**
  - Implements ADX (Average Directional Index) to confirm trend strength.
  - Confirms uptrend/downtrend strength using EMA alignment & ADX
  - Adding trend detection can help you:
  	- Avoid bad trades by filtering weak signals.
   	- Confirm strong buy/sell signals based on trend strength.
    - Hold your position instead of reacting to every small price movement.
  - Identifies Strong Uptrend, Strong Downtrend, or Weak/Ranging Markets using EMA alignment and ADX strength.
  - Determines if a trend is **strong (ADX > 25)** or **weak/ranging (ADX < 20)**.
  - Prevents false signals by avoiding trades in weak-trend conditions.

	#### **💡 Summary: Best ADX Filters**
| Filter | Condition | Purpose |
|--------|------------|---------|
| **ADX Threshold** | `df["ADX"] > 25` | Avoid weak trends |
| **ADX Slope** | `df["ADX"].diff() > 0` | Only trade strengthening trends |
| **EMA Confirmation** | `EMA50 > EMA200` (uptrend), `EMA50 < EMA200` (downtrend) | Confirm trend direction |
| **RSI Filter** | `RSI between 30-70` | Avoid overbought/oversold conditions |
| **Volume Confirmation** | `Volume > Avg_Volume` | Avoid false breakouts |
    
4. **Support & Resistance Detection**
  - Detects **price near support (Buy Zone) or resistance (Sell Zone)**.

 #### 🔷 **How Support & Resistance Work with EMA Crossovers**

| Scenario          | EMA Signal                                        | Support/Resistance Confirmation         | Action        |
|------------------|------------------------------------------------|----------------------------------------|--------------|
| 📈 **BUY**        | EMA 7 > EMA 21, EMA 21 > EMA 50                | Price bouncing from **support**       | 🔥 *Strong Buy* |
| 📉 **SELL**       | EMA 7 < EMA 21, EMA 21 < EMA 50                | Price rejected at **resistance**      | 🛑 *Strong Sell* |
| 🚀 **Breakout Buy**  | Price breaks above **resistance** & EMA 50, 100, 200 | 🔷 *Bullish confirmation*            | ✅ *Buy* |
| 🔻 **Breakdown Sell** | Price drops below **support** & EMA 50, 100, 200 | 🔻 *Bearish confirmation*            | ⚠️ *Sell/Short* |

5. **Volume-Based Signal Validation:**
  - Confirms breakouts using moving average of volume.
  - Compute Volume Moving Average (20-period)
  	- EMA7 & EMA21 → Confirms short-term momentum shifts.
   	- EMA21 & EMA50 → Mid-term confirmation of trend changes.
  - Volume Surge → Ensures crossovers are not false signals.

6. **Market Sentiment & Volume Analysis:**
	- Funding Rate Sentiment: Gauges long/short trader bias from Binance funding rates.
 	- Whale Activity Detection: Tracks abnormal volume movements to detect large trades. Identifies potential whale moves using Binance volume spikes and Bitcoin-specific Blockchair transaction data.

 
### 📡 **Automated Real-Time Alerts via Telegram**
- Sends **clear and meaningful** alerts in **Markdown format**.  
- Prevents **spam** by sending alerts only when conditions change.  
- Includes **price chart images** for better visualization.  

### ⚡ **Reliable Execution & Async Handling**
- Handles **async Telegram alerts** to avoid `asyncio` issues.  
- Uses **error handling** to prevent failures when sending messages.  
- Monitors multiple cryptocurrencies simultaneously.

### ⚖️ Confirmation-Based Trade Decision:
- Determines final BUY, SELL, or HOLD signals with at least 2 aligned indicators, factoring in trend strength and volume to minimize false positives.
- Trend Strength & Volume Filtering: Avoids weak/ranging market conditions.

### 🗄️ Redis Storage:
- Persistently stores messages, charts, and signal states with configurable TTL for efficient retrieval.

### 🔧 Customizable:
- Easily tweak settings like trend strength, monitoring intervals, and symbol lists via `settings.py`.
  
  
## 🔍 How It Works  
1. **Data Fetching**: Pulls real-time OHLCV data from Binance for configured symbols (e.g., BTC/USDT, WLD/USDT). 
2. **Indicator Calculation**: Computes technical indicators like EMAs, RSI, MACD, and ADX using the `util_indicators` module.  
3. **Signal Detection**: Analyzes indicators and whale activity via `util_signals` to generate individual signals (e.g., EMA crossovers, volume spikes). 
4. **Decision Logic**: Uses a confirmation-based strategy in `determine_trade_signal()`:
   - Requires at least 2 BUY or SELL signals to confirm a trade.
   - Incorporates ADX trend strength and volume to filter out noise.
   - Outputs a final status: BUY, SELL, or HOLD.
   - 🎯 Trading Decision Logic:
   
| Market Condition                                   | Decision                                                      |
|----------------------------------------------------|-------------------------------------------------------------|
| **Strong Uptrend, ADX > 25, High Volume**         | 🔥 **BUY** - Strong Uptrend with High Volume & ADX Confirmation |
| **Moderate Uptrend, ADX > 25**                    | ✅ **BUY** - Uptrend Confirmed with Strong ADX              |
| **Weak Uptrend, High Volume**                     | 📈 **BUY** - Uptrend Confirmed with High Volume             |
| **Strong Downtrend, ADX > 25, High Volume**       | 🛑 **SELL** - Strong Downtrend with High Volume & ADX Confirmation |
| **Moderate Downtrend, ADX > 25**                  | ❌ **SELL** - Downtrend Confirmed with Strong ADX           |
| **Weak Downtrend, High Volume**                   | 📉 **SELL** - Downtrend Confirmed with High Volume          |
| **Weak Trend, ADX < 20**                          | ⚠️ **HOLD** - Weak Trend, Low ADX (No Strong Signal)       |

5. **Alert Delivery**:
   - Posts a short summary to your Telegram group with current price and status.
   - Stores detailed analysis and charts in Redis, accessible via a "Read More" button.
6. **Scheduling**: Refreshes all symbols every 3 hours, with interim alerts triggered only on signal changes.

	- BUY: When at least 2 BUY signals align, with a strong uptrend & high volume.
 	- SELL: When at least 2 SELL signals align, with a strong downtrend & high volume.
  	- HOLD: If the market is weak (ADX < 20) or signals are unclear.

The result? Clear, actionable insights delivered straight to your Telegram, like this:

   <a href="https://ibb.co/tTqSP2N6"><img src="https://i.ibb.co/W4kQpzdX/SCR-20250217-lhfk.png" alt="SCR-20250217-lhfk" border="0"></a>
   - ChapGPT analysis: https://app.simplenote.com/p/X1ycfv
   - DeepSeek analysis: https://app.simplenote.com/p/S8VJN0
   - Grok analysis: https://app.simplenote.com/p/Nfv3kR
   - Google Gemini: http://simp.ly/p/GhhThM

     View the bot in action at <a href="https://t.me/+QOVsy-podHJhN2M9">Telegram</a> (version 13)

## 📂 **Setup Instructions**  
Follow these steps to get the Crypto Alert Bot up and running on your system. You’ll need Python, Redis, and a Telegram bot configured.

### Prerequisites
- **Python 3.8+**: Ensure Python is installed (`python --version`).
- **Redis Server**: For message and chart storage.
- **Telegram Bot**: For alerts and notifications.
- **Git**: To clone the repository.

### Step 1: Clone the Repository
   ```bash
	git clone https://github.com/ishafizan/crypto-alert-bot.git
	cd crypto-alert-bot
```

### Step 2: Install dependencies:  
   ```bash
   pip install -r requirements.txt
```
### Step 3: Set Up Redis
1. Install Redis:
- On Ubuntu: sudo apt update && sudo apt install redis-server
- On macOS: brew install redis
- On Windows: Use WSL or a Redis Docker container (docker run -d -p 6379:6379 redis).
	- https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/install-redis-on-windows/
2. Start Redis:
  ```bash
  redis-server
  ```
Ensure it’s running on localhost:6379 (default). Test with redis-cli ping (should return "PONG").

### Step 4: Configure Telegram Bot
1.  To create a Telegram bot token
    - Open the Telegram app
    - Search for "@BotFather"
    - Start a chat with BotFather
    - Type /newbot
    - Follow the instructions to name and username your bot
    - BotFather will send you a unique API token
2. To create a chat ID
    - Create a new chat group
    - Add your bot to the group
    - Go to Telegram Web and log in to your account
    - Select the group chat
    - The chat ID (numbers/digits) is in the URL in the address bar

### Step 5: Configure Telegram Bot

Edit settings.py with your details:
   ```python
# settings.py
TELEGRAM_BOT_TOKEN = "your_bot_token_here"  # From BotFather
TELEGRAM_CHAT_ID = "your_chat_id_here"     # Group chat ID
SEND_CHAT = True                           # Enable Telegram alerts
BOT_USERNAME = "YourBotUsername"           # Bot's Telegram username
SYMBOLS = ["BTCUSDT", "ETHUSDT", "WLDUSDT"] # Symbols to monitor
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0
MESSAGE_TTL = 3600  # Message lifespan in seconds (1 hour)
MONITOR_SLEEP = 300  # Check interval in seconds (5 minutes)
MIN_TREND_STRENGTH = "Moderate"  # Options: "Weak", "Moderate", "Strong"
TREND_CONFIG = {
    "Weak": {"EMA_PERIODS": [9, 21, 50], "ADX_THRESHOLD": 20, "BREAKOUT_PERCENTAGE": 0.01, "VOLUME_MULTIPLIER": 2.5, "ATR_MULTIPLIER": 1.5, "RSI_PERIOD": 14},
    "Moderate": {"EMA_PERIODS": [9, 21, 50, 100], "ADX_THRESHOLD": 25, "BREAKOUT_PERCENTAGE": 0.015, "VOLUME_MULTIPLIER": 2.0, "ATR_MULTIPLIER": 2.0, "RSI_PERIOD": 14},
    "Strong": {"EMA_PERIODS": [9, 21, 50, 100, 200], "ADX_THRESHOLD": 30, "BREAKOUT_PERCENTAGE": 0.02, "VOLUME_MULTIPLIER": 1.5, "ATR_MULTIPLIER": 2.5, "RSI_PERIOD": 14}
}
CLEAR_REDIS_ON_SHUTDOWN = True
```
	
## 📂 How To Run
1. Start Redis: Ensure Redis is running (redis-server in a separate terminal).
2. **Run the BOT**
```bash
python crypto_alert_bot.py
```
3. Monitor Alerts:

- Check your Telegram group for initial alerts.
- Click "Read More" to view detailed analysis in a private chat with your bot.
- Stop the Bot: Press Ctrl+C to gracefully shut down (clears Redis if configured).
    
## 📌 What I DID NOT do
- Add automatic order execution to buy/sell directly on Binance. 
- Can do if there's a safe sandbox i can play around. Do it manually-lah for now, jgn malas 😂

## 📌 Others

1. **Trade Confidence & Signal Strength**

	✅ Signal Strength Meter – Assign confidence levels to signals (e.g., weak/medium/strong) based on multiple confirmations. 

	✅ Trend Score – Score from 1 to 100 based on EMAs, RSI, and momentum. Helps gauge bullish/bearish strength. 

| Trend Score | Message                                      |
|------------|----------------------------------------------|
| **0-20**   | "Very weak trend, choppy price action."     |
| **21-40**  | "Weak trend, avoid trading in ranging markets." |
| **41-60**  | "Moderate trend, potential setups forming." |
| **61-80**  | "Strong trend detected, possible breakout soon." |
| **81-100** | "Very strong trend, momentum is high!"      | 	


3. **Additional Market Insights**

	✅ Volume Analysis – Identify spikes in buying/selling volume to confirm trend strength. 

		Compute Volume Moving Average (20-period)
			•	EMA7 & EMA21 → Confirms short-term momentum shifts.
			•	EMA21 & EMA50 → Mid-term confirmation of trend changes.
			•	Volume Surge → Ensures crossovers are not false signals.

	✅ Volatility Indicator – Show if the market is trending or ranging to avoid fakeouts.

	✅ MACD Indicator – Add another confirmation layer to trend shifts. 

| Indicator        | Signal Mechanism                          | How It Relates |
|-----------------|-----------------------------------------|---------------|
| **EMA Crossovers** | When `EMA_Short` crosses `EMA_Long` | This is **exactly** when the **MACD Line crosses zero**. |
| **MACD Line**   | Difference between `EMA_Short` and `EMA_Long` | Positive MACD means bullish momentum (above zero), negative MACD means bearish (below zero). |
| **Signal Line** | 9-period EMA of MACD Line | Helps filter out false signals. |
| **MACD Histogram** | MACD Line - Signal Line | Highlights strength and confirmation of the trend. |



# Disclaimer

This software is for educational purposes only. Do not risk money which you are afraid to lose. 

USE THE SOFTWARE AT YOUR OWN RISK. THE AUTHOR AND ALL AFFILIATES ASSUME NO RESPONSIBILITY FOR YOUR TRADING RESULTS.

Always start by running a trading bot in Dry-run and do not engage money before you understand how it works and what profit/loss you should expect.

I strongly recommend you to have coding and Python knowledge. 

Do not hesitate to read the source code and understand the mechanism of this bot.
 
  
  


  
