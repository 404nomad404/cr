# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

__author__ = 'Ishafizan'
__date__: "15 Feb 2025"

from datetime import datetime, timedelta
import requests
import pandas as pd
import settings
from utils.util_log import logger

log = logger()


def fetch_binance_data(symbol, interval="1d", limit=settings.BINANCE_HISTORICAL_DATA, start_date=None, end_date=None):
    """
    Fetch historical OHLCV data from Binance API.

    Parameters:
    - symbol (str): Trading pair symbol (e.g., "BTCUSDT").
    - interval (str): Timeframe (e.g., "1d", "4h", "1h").
    - limit (int): Number of data points to fetch.
    - start_date (str or None): Start date in "YYYY-MM-DD" format (optional).
    - end_date (str or None): End date in "YYYY-MM-DD" format (optional).

    Returns:
    - pd.DataFrame: DataFrame containing open, high, low, close, volume with timestamps as index.
    """

    url = f"{settings.BINANCE_URL}?symbol={symbol}&interval={interval}&limit={limit}"
    response = requests.get(url)
    data = response.json()

    # Convert response into DataFrame
    df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close", "volume", "close_time",
                                     "quote_asset_volume", "trades", "taker_base_volume", "taker_quote_volume",
                                     "ignore"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

    # Convert to numeric
    df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
    df.set_index("timestamp", inplace=True)

    # 🔹 **Filter by date range (if provided)**
    if start_date:
        df = df[df.index >= pd.to_datetime(start_date)]
    if end_date:
        df = df[df.index <= pd.to_datetime(end_date)]

    return df[['open', 'high', 'low', 'close', 'volume']]


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


def fetch_blockchain_exchange_flows(exchange_address="1Kr6QSydW9bFQG1mXiPNNu6WpJGmUa9i1g"):  # Example: Kraken wallet
    url = f"https://blockchain.info/q/addressbalance/{exchange_address}"
    response = requests.get(url)
    return float(response.text) / 1e8  # Convert satoshis to BTC


def fetch_coinmetrics_exchange_flows(asset="btc"):  # Ensure asset parameter is included
    url = "https://community-api.coinmetrics.io/v4/timeseries/asset-metrics"
    params = {"assets": asset, "metrics": "FlowInExchgUSD,FlowOutExchgUSD", "frequency": "1d"}
    try:
        log.info(f"Fetching CoinMetrics data for {asset} from {url} with params {params}")
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if "data" not in data:
            log.warning(f"CoinMetrics response missing 'data' key for {asset}")
            return pd.DataFrame()
        df = pd.DataFrame(data["data"])
        df["FlowInExchgUSD"] = pd.to_numeric(df["FlowInExchgUSD"], errors="coerce")
        df["FlowOutExchgUSD"] = pd.to_numeric(df["FlowOutExchgUSD"], errors="coerce")
        log.info(f"CoinMetrics exchange flows fetched successfully for {asset}")
        return df
    except requests.exceptions.RequestException as e:
        log.error(f"Network error fetching CoinMetrics flows for {asset}: {e}")
        return pd.DataFrame()
    except Exception as e:
        log.error(f"Unexpected error fetching CoinMetrics flows for {asset}: {e}")
        return pd.DataFrame()


def fetch_binance_funding_rates2(symbol="BTCUSDT"):
    url = "https://fapi.binance.com/fapi/v1/fundingRate"
    params = {"symbol": symbol, "limit": 10}
    response = requests.get(url, params=params)
    return pd.DataFrame(response.json())


import nasdaqdatalink


def fetch_cme_open_interest():
    try:
        nasdaqdatalink.ApiConfig.api_key = settings.QUANDL_API_KEY
        log.info(f"Fetching CME Open Interest with API key: {settings.QUANDL_API_KEY[:4]}... (masked)")
        data = nasdaqdatalink.get("CHRIS/CME_BTC1", rows=10)
        if data.empty:
            log.warning("CME OI data returned empty")
            return None
        oi = data["Open Interest"].iloc[-1]
        log.info(f"CME Open Interest fetched: {oi}")
        return oi
    except nasdaqdatalink.AuthenticationError as e:
        log.error(f"CME OI fetch failed due to authentication: {e}")
        return None
    except Exception as e:
        log.error(f"Error fetching CME OI: {e}")
        return None


def fetch_blockchair_whale_txns(min_value=1000):
    url = f"https://api.blockchair.com/bitcoin/transactions?limit=10&value_gte={min_value * 1e8}"
    try:
        log.info(f"Fetching Blockchair whale transactions from {url}")
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        # log.debug(f"Blockchair response: {data}")
        if "data" not in data or not data["data"]:
            log.warning("Blockchair response missing 'data' or empty")
            return []
        txns = data["data"]
        whale_txns = []
        for tx in txns:
            try:
                amount = tx.get("value", 0) / 1e8  # Use .get() to avoid KeyError
                whale_txns.append({
                    "amount": amount,
                    "from": tx.get("inputs", []),
                    "to": tx.get("outputs", [])
                })
            except Exception as e:
                log.error(f"Error parsing Blockchair transaction: {e}")
        log.info(f"Fetched {len(whale_txns)} whale transactions")
        return whale_txns
    except requests.exceptions.RequestException as e:
        log.error(f"Network error fetching Blockchair txns: {e}")
        return []
    except Exception as e:
        log.error(f"Unexpected error fetching Blockchair txns: {e}")
        return []


def fetch_deribit_extended_data(symbol="BTC"):
    url = f"{settings.DERIBIT_URL}get_order_book"
    params = {"instrument_name": f"BTC-PERPETUAL"}
    response = requests.get(url, params=params)
    return response.json()["result"]


def fetch_binance_open_interest(symbol="BTCUSDT"):
    url = "https://fapi.binance.com/fapi/v1/openInterest"
    params = {"symbol": symbol}
    response = requests.get(url, params=params)
    data = response.json()
    return float(data["openInterest"]) if "openInterest" in data else None


def fetch_binance_volume(symbol="BTCUSDT"):
    """
    Fetch recent trading volume from Binance for whale activity detection.
    """
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": "1d", "limit": 2}  # Last 2 days for comparison
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close", "volume", "close_time",
                                         "quote_asset_volume", "trades", "taker_base_volume", "taker_quote_volume", "ignore"])
        df["volume"] = df["volume"].astype(float)
        log.info(f"Binance volume fetched successfully for {symbol}")
        return df[["timestamp", "volume"]]
    except Exception as e:
        log.error(f"Error fetching Binance volume for {symbol}: {e}")
        return pd.DataFrame()
