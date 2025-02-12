# -*- coding: utf-8 -*-
__author__ = 'Ishafizan'
__date__ = "12 Feb 2025"
"""
This script:
	•	Fetches historical data from Binance
	•	Computes EMAs (7, 21, 50, 100, 200)
	•	Implements buy/sell logic based on your requested criteria
	•	Simulates trades and calculates final balance, profit/loss, win rate, and trade logs
	•	Plots the price, EMAs, and buy/sell signals
"""
import os, sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
sys.path.append(BASE_DIR)
import settings
from utils import util_log

# instantiate logger
log = util_log.logger()


# Binance API URL for fetching historical data
def fetch_binance_data(symbol, interval="1d", limit=1000):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    response = requests.get(url)
    data = response.json()

    # Convert data into a DataFrame
    df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close", "volume", "close_time",
                                     "quote_asset_volume", "trades", "taker_base_volume", "taker_quote_volume",
                                     "ignore"])

    # Convert relevant columns to numeric and timestamp to datetime
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df["close"] = df["close"].astype(float)
    df.set_index("timestamp", inplace=True)

    return df[["close"]]  # Only keep the closing prices


# Ask user for the crypto pair
symbol = input("Enter the crypto pair (e.g., BTCUSDT, ETHUSDT, WLDUSDT): ").upper()
df = fetch_binance_data(symbol)

# Calculate Exponential Moving Averages (EMA)
df["EMA7"] = df["close"].ewm(span=7, adjust=False).mean()
df["EMA21"] = df["close"].ewm(span=21, adjust=False).mean()
df["EMA50"] = df["close"].ewm(span=50, adjust=False).mean()
df["EMA100"] = df["close"].ewm(span=100, adjust=False).mean()
df["EMA200"] = df["close"].ewm(span=200, adjust=False).mean()

# Generate BUY/SELL signals based on EMA crossovers
df["Signal"] = np.nan
# BUY
df.loc[(df["EMA7"] > df["EMA21"]) & (df["EMA7"].shift(1) <= df["EMA21"].shift(1)), "Signal"] = "BUY"
# SELL
df.loc[(df["EMA7"] < df["EMA21"]) & (df["EMA7"].shift(1) >= df["EMA21"].shift(1)), "Signal"] = "SELL"

# Filter BUY & SELL signals
buy_signals = df[df["Signal"] == "BUY"]
sell_signals = df[df["Signal"] == "SELL"]

# Backtesting Variables
initial_balance = settings.INITIAL_BALANCE  # Starting balance in USD
balance = initial_balance
position = 0  # Number of crypto units held
trade_log = []
win_count = 0
loss_count = 0

# Simulated Trading Execution
for index, row in df.iterrows():
    if row["Signal"] == "BUY" and balance > 0:
        position = balance / row["close"]  # Buy crypto with full balance
        balance = 0
        trade_log.append((index, "BUY", row["close"]))

    elif row["Signal"] == "SELL" and position > 0:
        balance = position * row["close"]  # Sell all crypto
        profit_loss = balance - initial_balance
        trade_log.append((index, "SELL", row["close"], profit_loss))

        # Win/Loss Tracking
        if profit_loss > 0:
            win_count += 1
        else:
            loss_count += 1

        position = 0

# Final Balance Calculation
final_balance = balance if balance > 0 else position * df["close"].iloc[-1]  # If still holding, sell at last price
profit_loss = final_balance - initial_balance
win_rate = (win_count / max(1, (win_count + loss_count))) * 100  # Avoid division by zero

# Display Backtest Results
log.info("\nBacktest Summary:")
log.info(f"Initial Balance: ${initial_balance:.2f}")
log.info(f"Final Balance: ${final_balance:.2f}")
log.info(f"Profit/Loss: ${profit_loss:.2f}")
log.info(f"Win Rate: {win_rate:.2f}%")
log.info("\nTrade Log:")
for trade in trade_log:
    log.info(trade)

# Plot price and EMA lines
plt.figure(figsize=(12, 6))
plt.plot(df.index, df["close"], label="Price", color="blue", alpha=0.7, zorder=1)
plt.plot(df.index, df["EMA7"], label="EMA7", color="cyan", linestyle="dashed", alpha=0.7)
plt.plot(df.index, df["EMA21"], label="EMA21", color="magenta", linestyle="dashed", alpha=0.7)
plt.plot(df.index, df["EMA50"], label="EMA50", color="orange", linestyle="dashed", alpha=0.7)
plt.plot(df.index, df["EMA100"], label="EMA100", color="purple", linestyle="dashed", alpha=0.7)
plt.plot(df.index, df["EMA200"], label="EMA200", color="brown", linestyle="dashed", alpha=0.7)

# Plot BUY and SELL markers
plt.scatter(buy_signals.index, buy_signals["close"], marker="^", color="green", s=120, label="BUY", edgecolors='black',
            zorder=3)
plt.scatter(sell_signals.index, sell_signals["close"], marker="v", color="red", s=120, label="SELL", edgecolors='black',
            zorder=3)

# Title and legend
plt.title(f"Backtest Results for {symbol}")
plt.legend()
plt.xticks(rotation=45)
plt.show()
