
# 📊 Crypto Monitoring & Alert Bot 🚀  

## Overview  
This Python script integrates **Binance API** and **Telegram** to monitor cryptocurrency prices, detect trading signals, and send real-time alerts with price charts. 

It helps traders identify **EMA crossovers, RSI signals, and trend strength** to make informed trading decisions.  

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
 	- Whale Activity Detection: Tracks abnormal volume movements to detect large trades.

 
### 📡 **Automated Real-Time Alerts via Telegram**
- Sends **clear and meaningful** alerts in **Markdown format**.  
- Prevents **spam** by sending alerts only when conditions change.  
- Includes **price chart images** for better visualization.  

### ⚡ **Reliable Execution & Async Handling**
- Handles **async Telegram alerts** to avoid `asyncio` issues.  
- Uses **error handling** to prevent failures when sending messages.  
- Monitors multiple cryptocurrencies simultaneously.

### ✅ Confirmation-Based Trade Decision:
- At least two indicators must confirm a BUY/SELL before making a decision.
- Trend Strength & Volume Filtering: Avoids weak/ranging market conditions.
  
## 🚀 How It Works  
1. Fetches **live price data** from Binance API every 15 minutes.  
2. Computes **technical indicators.  
3. Detects **buy/sell signals** based on indicator crossovers & trend confirmation.  
4. Sends **real-time alerts to Telegram** with charts.
5. 🎯 Final Trading Decision Logic:
   

| Market Condition                                   | Decision                                                      |
|----------------------------------------------------|-------------------------------------------------------------|
| **Strong Uptrend, ADX > 25, High Volume**         | 🔥 **BUY** - Strong Uptrend with High Volume & ADX Confirmation |
| **Moderate Uptrend, ADX > 25**                    | ✅ **BUY** - Uptrend Confirmed with Strong ADX              |
| **Weak Uptrend, High Volume**                     | 📈 **BUY** - Uptrend Confirmed with High Volume             |
| **Strong Downtrend, ADX > 25, High Volume**       | 🛑 **SELL** - Strong Downtrend with High Volume & ADX Confirmation |
| **Moderate Downtrend, ADX > 25**                  | ❌ **SELL** - Downtrend Confirmed with Strong ADX           |
| **Weak Downtrend, High Volume**                   | 📉 **SELL** - Downtrend Confirmed with High Volume          |
| **Weak Trend, ADX < 20**                          | ⚠️ **HOLD** - Weak Trend, Low ADX (No Strong Signal)       |

	- BUY: When at least 2 BUY signals align, with a strong uptrend & high volume.
 	- SELL: When at least 2 SELL signals align, with a strong downtrend & high volume.
  	- HOLD: If the market is weak (ADX < 20) or signals are unclear.
7. The system ensures alerts are only sent when new conditions appear to prevent redundant notifications.

## 📂 **Setup Instructions**  
1. Install dependencies:  
   ```bash
   pip install -r requirements.txt
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

	✅ Sends detailed Telegram alerts including price, trend, and reasoning

	✅ Attaches a small trend chart

	✅ Helps visualize price movement before making decisions.

   <a href="https://ibb.co/tTqSP2N6"><img src="https://i.ibb.co/W4kQpzdX/SCR-20250217-lhfk.png" alt="SCR-20250217-lhfk" border="0"></a>
      
   View the bot in action at <a href="https://t.me/+QOVsy-podHJhN2M9">Telegram</a> (version 8)
   


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

	✅ Signal Strength Meter – Assign confidence levels to signals (e.g., weak/medium/strong) based on multiple confirmations. (Done)

	✅ Trend Score – Score from 1 to 100 based on EMAs, RSI, and momentum. Helps gauge bullish/bearish strength. (Done)

| Trend Score | Message                                      |
|------------|----------------------------------------------|
| **0-20**   | "Very weak trend, choppy price action."     |
| **21-40**  | "Weak trend, avoid trading in ranging markets." |
| **41-60**  | "Moderate trend, potential setups forming." |
| **61-80**  | "Strong trend detected, possible breakout soon." |
| **81-100** | "Very strong trend, momentum is high!"      | 	


3. **Additional Market Insights**

	✅ Volume Analysis – Identify spikes in buying/selling volume to confirm trend strength. (Done)

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


5. **Improved Alerts & Decision Support**

	✅ Risk/Reward Estimation – Suggest optimal entry price, stop-loss, and take-profit levels. (*KIV*)

		Issues:
   			1. If there are no EMA crossovers, ATR-based stop-loss/take-profit might not be triggered
			2. If the price is too far from past signals, they get discarded
   			3. Entry Price is Too Different from Current Price
   			4. Some signals might not have valid ATR-based stop-loss/take-profit calculations, causing them to be ignored.

	✅ Support/Resistance Breakout Detection – Alert when price breaks past key levels instead of just touching them. (Done)

		Why is Breakout Detection Important?

			1.	Prevents False Signals – Many times, the price tests a support/resistance level but reverses quickly. A proper breakout confirmation helps you avoid fakeouts.
			2.	Stronger Trend Confirmation – When price breaks a key level with volume and momentum, it often signals a strong trend continuation or reversal.
			3.	Better Trade Timing – Waiting for a confirmed breakout can help enter trades at the right time instead of getting caught in a range.

	✅ Whale Activity Alert – Detect unusual buy/sell volume spikes indicating large trader moves. (Done)

		- Whales buy before big rallies & sell before crashes. Detecting their activity gives you a head start on potential price swings.
		- Low-volume breakouts are often fakeouts—whales may trap retail traders before dumping

	✅ Market Sentiment Check – Integrate data from sources like Binance funding rates to gauge trader sentiment. (Done)

		1. Improve Buy/Sell Timing
   			- If RSI is oversold but funding rates remain negative, the downtrend might continue.
   			- If EMA crossovers suggest a buy, but funding rates are highly negative, waiting for sentiment improvement can reduce false trades.
   			- Avoiding Traps – Extreme funding rates may indicate overleveraged positions, leading to potential liquidations and reversals
   
   		2.	Filter False Breakouts
   			- A breakout with negative funding rates might be a short squeeze, indicating a potential reversal
   
   		3. Identify Bullish vs. Bearish Sentiment
			- Positive funding rates → More demand for long positions → Bullish sentiment
			- Negative funding rates → More demand for short positions → Bearish sentiment
   
		4. Understanding Market Bias
   			– Positive funding rates indicate long dominance (bullish sentiment), while negative rates suggest short dominance (bearish sentiment).
   			- If buy signals align with positive sentiment (longs paying shorts), it adds confluence to decisions made.
     	

6. User Customization

	✅ Adjustable Thresholds – Allow you to tweak RSI, EMA crossovers, and risk levels dynamically.

	✅ Multi-Crypto Filtering – Rank and sort monitored cryptos based on trend strength.


# Disclaimer

This software is for educational purposes only. Do not risk money which you are afraid to lose. 

USE THE SOFTWARE AT YOUR OWN RISK. THE AUTHOR AND ALL AFFILIATES ASSUME NO RESPONSIBILITY FOR YOUR TRADING RESULTS.

Always start by running a trading bot in Dry-run and do not engage money before you understand how it works and what profit/loss you should expect.

I strongly recommend you to have coding and Python knowledge. 

Do not hesitate to read the source code and understand the mechanism of this bot.
 
  
  


  
