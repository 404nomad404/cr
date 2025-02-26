# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io
from matplotlib.collections import LineCollection


def generate_price_chart(df, symbol, sha_timestamp=None, sha_action=None):
    """
    Generate a multi-panel price chart with EMA crossovers, Smoothed Heikin Ashi (SHA) candlesticks,
    RSI, and ADX indicators, highlighting SHA buy/sell signals with markers.

    Parameters:
    df (DataFrame): Price data including close price, EMAs, SHA, RSI, and ADX values.
    symbol (str): The cryptocurrency symbol being analyzed.
    sha_timestamp (datetime, optional): Timestamp of the latest SHA signal.
    sha_action (str, optional): Action of the latest SHA signal ('BUY' or 'SELL').

    Returns:
    BytesIO: Image of the generated price chart.
    """
    # Display last 300 data points for deeper trend visualization
    df = df.tail(300)
    dates = df.index

    # Create a figure with 3 vertically stacked subplots
    fig, ax = plt.subplots(3, 1, figsize=(14, 12), sharex=True, gridspec_kw={'height_ratios': [2, 1, 1]})

    # ---- Price & EMA Crossovers with SHA Candlesticks ----
    # Plot closing price
    ax[0].plot(dates, df["close"], label="Price", color="blue", linewidth=2)

    # Plot EMAs
    ax[0].plot(dates, df["EMA21"], label="EMA21 (Short-term)", color="green", linestyle="dashed")
    ax[0].plot(dates, df["EMA50"], label="EMA50 (Mid-term)", color="orange", linestyle="dashed")
    ax[0].plot(dates, df["EMA100"], label="EMA100 (Long-term)", color="red", linestyle="dashed")
    ax[0].plot(dates, df["EMA200"], label="EMA200 (Very Long-term)", color="purple", linestyle="dashed")

    # Plot SHA Candlesticks (enhanced lines)
    x = mdates.date2num(dates)
    segments = []
    colors = []
    for i in range(len(df)):
        open_price = df['SHA_Open'].iloc[i]
        close_price = df['SHA_Close'].iloc[i]
        high_price = df['SHA_High'].iloc[i]
        low_price = df['SHA_Low'].iloc[i]
        segments.append([(x[i], low_price), (x[i], high_price)])  # Wick
        segments.append([(x[i], open_price), (x[i], close_price)])  # Body
        color = 'green' if close_price > open_price else 'red'
        colors.extend([color, color])  # Same color for wick and body

    # Adjusted linewidths for better clarity
    candlesticks = LineCollection(segments, colors=colors, linewidths=(1.8, 4.5),
                                  linestyle='solid', alpha=0.8, label="SHA Candlesticks")
    ax[0].add_collection(candlesticks)

    # Add SHA buy/sell signal markers if provided
    if sha_timestamp and sha_action:
        sha_date = mdates.date2num(sha_timestamp)
        if sha_action == "BUY":
            ax[0].plot(sha_date, df.loc[sha_timestamp, "close"], marker='^', markersize=10,
                       color="green",
                       label="SHA BUY Signal" if "SHA BUY Signal" not in ax[0].get_legend_handles_labels()[1] else "")
        elif sha_action == "SELL":
            ax[0].plot(sha_date, df.loc[sha_timestamp, "close"], marker='v', markersize=10,
                       color="red",
                       label="SHA SELL Signal" if "SHA SELL Signal" not in ax[0].get_legend_handles_labels()[1] else "")

    # Set y-axis limits based on SHA range
    ax[0].set_ylim(min(df['SHA_Low'].min(), df['close'].min()) * 0.95,
                   max(df['SHA_High'].max(), df['close'].max()) * 1.05)

    ax[0].set_title(f"{symbol} Price, EMA Crossovers & SHA Candlesticks")
    ax[0].set_ylabel("Price (USDT)")
    ax[0].grid(True)
    ax[0].legend()

    # ---- RSI (Relative Strength Index) ----
    ax[1].plot(dates, df["RSI"], label="RSI", color="purple")
    ax[1].axhline(70, linestyle="dashed", color="red", alpha=0.5, label="Overbought (70)")
    ax[1].axhline(30, linestyle="dashed", color="green", alpha=0.5, label="Oversold (30)")
    ax[1].set_title("Relative Strength Index (RSI)")
    ax[1].set_ylabel("RSI")
    ax[1].grid(True)
    ax[1].legend()

    # ---- ADX (Average Directional Index) ----
    ax[2].plot(dates, df["ADX"], label="ADX", color="black")
    ax[2].axhline(25, linestyle="dashed", color="gray", alpha=0.5, label="Trend Strength (25)")
    ax[2].set_title("Average Directional Index (ADX)")
    ax[2].set_xlabel("Time")
    ax[2].set_ylabel("ADX")
    ax[2].grid(True)
    ax[2].legend()

    # ---- Format x-axis ----
    plt.xticks(rotation=45)
    ax[2].xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
    ax[2].xaxis.set_major_locator(mdates.AutoDateLocator())

    # Save and return the chart
    img = io.BytesIO()
    plt.tight_layout()
    plt.savefig(img, format="png", bbox_inches="tight", dpi=200)
    img.seek(0)
    plt.close()
    return img
