# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

__author__ = 'Ishafizan'
__date__: "15 Feb 2025"

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io


def generate_price_chart(df, symbol):
    """
    Generate a multi-panel price chart with EMA crossovers, RSI, and ADX indicators.

    Parameters:
    df (DataFrame): The price data including close price, EMAs, RSI, and ADX values.
    symbol (str): The symbol of the cryptocurrency being analyzed.

    Returns:
    BytesIO: A BytesIO object containing the generated price chart image.
    """

    # Create a figure with 3 subplots arranged vertically
    fig, ax = plt.subplots(3, 1, figsize=(10, 8), sharex=True, gridspec_kw={'height_ratios': [2, 1, 1]})

    # ---- Price & EMA Crossovers ----
    # Plot the closing price and different Exponential Moving Averages (EMAs)
    ax[0].plot(df.index[-100:], df["close"].tail(100), label="Price", color="blue", linewidth=2)
    ax[0].plot(df.index[-100:], df["EMA21"].tail(100), label="EMA21 (Short-term)", color="green", linestyle="dashed")
    ax[0].plot(df.index[-100:], df["EMA50"].tail(100), label="EMA50 (Mid-term)", color="orange", linestyle="dashed")
    ax[0].plot(df.index[-100:], df["EMA100"].tail(100), label="EMA100 (Long-term)", color="red", linestyle="dashed")
    ax[0].plot(df.index[-100:], df["EMA200"].tail(100), label="EMA200 (Very Long-term)", color="purple",
               linestyle="dashed")

    ax[0].set_title(f"{symbol} Price & EMA Crossovers")
    ax[0].set_ylabel("Price (USDT)")
    ax[0].grid(True)
    ax[0].legend()

    # ---- RSI (Relative Strength Index) Plot ----
    # RSI is used to identify overbought and oversold conditions
    ax[1].plot(df.index[-100:], df["RSI"].tail(100), label="RSI", color="purple")
    ax[1].axhline(70, linestyle="dashed", color="red", alpha=0.5, label="Overbought (70)")  # Overbought level
    ax[1].axhline(30, linestyle="dashed", color="green", alpha=0.5, label="Oversold (30)")  # Oversold level
    ax[1].set_title("Relative Strength Index (RSI)")
    ax[1].set_ylabel("RSI Value")
    ax[1].grid(True)
    ax[1].legend()

    # ---- ADX (Average Directional Index) Plot ----
    # ADX measures the strength of a trend (above 25 indicates a strong trend)
    ax[2].plot(df.index[-100:], df["ADX"].tail(100), label="ADX", color="black")
    ax[2].axhline(25, linestyle="dashed", color="gray", alpha=0.5,
                  label="Trend Strength Threshold (25)")  # ADX threshold for strong trends
    ax[2].set_title("Average Directional Index (ADX)")
    ax[2].set_xlabel("Time")
    ax[2].set_ylabel("ADX Value")
    ax[2].grid(True)
    ax[2].legend()

    # ---- Format x-axis for better readability ----
    plt.xticks(rotation=45)  # Rotate x-axis labels for clarity
    ax[2].xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))  # Format date labels
    ax[2].xaxis.set_major_locator(mdates.AutoDateLocator())  # Auto-adjust date labels

    # ---- Save chart to a BytesIO object ----
    img = io.BytesIO()  # Create an in-memory bytes buffer
    plt.tight_layout()  # Adjust layout for better spacing
    plt.savefig(img, format="png", bbox_inches="tight", dpi=200)  # Save figure as a PNG image
    img.seek(0)  # Move the buffer cursor to the start
    plt.close()  # Close the figure to free memory
    return img  # Return the image buffer
