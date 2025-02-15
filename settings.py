# -*- coding: utf-8 -*-

__author__ = 'Ishafizan'
__date__: "12 Feb 2025"


# ----------------------------------------------
# Binance API Configuration (Public API)
BINANCE_API_KEY = ""  # No need for a private key since we're only reading market data
BINANCE_SECRET_KEY = ""

# Binance API URL
BINANCE_URL = "https://api.binance.com/api/v3/klines"
BINANCE_FUNDINGRATE = "https://fapi.binance.com/fapi/v1/fundingRate"
BINANCE_FUNDINGRATE_LIMIT = 10  # Fetch data for the latest 10 funding rates

# Historical data
BINANCE_HISTORICAL_DATA = 500  # set limit

# ----------------------------------------------
# Telegram Configuration
TELEGRAM_BOT_TOKEN = ""
# TELEGRAM_CHAT_ID = "6486852324"  # send to BOT
TELEGRAM_CHAT_ID = ""  # send to GROUP

# ----------------------------------------------
# CRYPTOs to monitor
SYMBOLS = ["BNBUSDT", "THETAUSDT", "SOLUSDT", "WLDUSDT", "XRPUSDT", "ETHUSDT", "BTCUSDT"]

# ----------------------------------------------
# Backtest
INITIAL_BALANCE = 1000
