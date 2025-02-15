# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

__author__ = 'Ishafizan'
__date__: "15 Feb 2025"

import numpy as np
import pandas as pd
import settings
import requests
from datetime import datetime, timedelta


# Fetch historical data
def fetch_binance_data(symbol, interval="1d", limit=settings.BINANCE_HISTORICAL_DATA):
    url = f"{settings.BINANCE_URL}?symbol={symbol}&interval={interval}&limit={limit}"
    response = requests.get(url)
    data = response.json()
    df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close", "volume", "close_time",
                                     "quote_asset_volume", "trades", "taker_base_volume", "taker_quote_volume",
                                     "ignore"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    # Convert to numeric
    df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
    df.set_index("timestamp", inplace=True)
    return df[['open', 'high', 'low', 'close', 'volume']]


def fetch_binance_funding_rates():
    """
    Fetches the latest funding rates from Binance for market sentiment analysis.
    """
    url = settings.BINANCE_FUNDINGRATE
    params = {"limit": 10}  # Fetch data for the latest 10 funding rates

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raises an error for bad responses (4xx and 5xx)
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching funding rates: {e}")
        return None


def fetch_binance_funding_rates2(symbol="BTCUSDT", days=30):
    """
    Fetch historical funding rates for a given symbol from Binance Futures API.
    """
    url = settings.BINANCE_FUNDINGRATE  # "https://fapi.binance.com/fapi/v1/fundingRate"
    end_time = int(datetime.now().timestamp() * 1000)  # Current time in milliseconds
    start_time = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)  # Start time

    params = {
        "symbol": symbol,
        "startTime": start_time,
        "endTime": end_time,
        "limit": 1000  # Max records per request
    }

    response = requests.get(url, params=params)
    data = response.json()

    # Convert data to DataFrame
    df = pd.DataFrame(data)
    df["fundingRate"] = df["fundingRate"].astype(float)
    df["time"] = pd.to_datetime(df["time"], unit="ms")
    df = df[["time", "fundingRate"]]  # Keep only relevant columns

    return df


def fetch_binance_funding_rates(symbol, limit=1000):
    """
    Fetches the last 30 days of funding rates for a given symbol from Binance Futures API.
    """
    url = "https://fapi.binance.com/fapi/v1/fundingRate"
    params = {"symbol": symbol.upper(), "limit": limit}
    response = requests.get(url, params=params)

    if response.status_code != 200:
        print("Error fetching data:", response.text)
        return None

    data = response.json()
    # print(data)

    # Convert to DataFrame
    df = pd.DataFrame(data)
    df["fundingRate"] = df["fundingRate"].astype(float)
    df["time"] = pd.to_datetime(df["fundingTime"], unit="ms")

    return df[["time", "fundingRate"]]

# Example Usage:
# btc_funding_rates = fetch_binance_funding_rates("BTCUSDT", days=30)
# print(btc_funding_rates.head())
