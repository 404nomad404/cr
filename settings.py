# -*- coding: utf-8 -*-

__author__ = 'Ishafizan'
__date__: "12 Feb 2025"

"""
https://github.com/ishafizan/CRYPTO-BUY-SELL-HOLD-SIGNALS-AND-ALERTS/blob/main/README.md
"""

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

# New Data Sources
DERIBIT_URL = "https://www.deribit.com/api/v2/public/"
BLOCKCHAIN_URL = "https://blockchain.info/"
COINMETRICS_URL = "https://community-api.coinmetrics.io/v4/"
BLOCKCHAIR_URL = "https://api.blockchair.com/bitcoin/"
QUANDL_API_KEY = ""  # https://docs.data.nasdaq.com/v1.0/docs/getting-started

# ----------------------------------------------
# Telegram Configuration
TELEGRAM_BOT_TOKEN = "your_bot_token_here"
TELEGRAM_CHAT_ID = "your_chat_id_here"  # send directly to BOT
BOT_USERNAME = "YourBotUsername"  # Name of BOT

SEND_CHAT = True  # send alerts
MONITOR_SLEEP = (60 * 15)  # 900  # set 900 fifteen minutes
REFRESH_INTERVAL = (60 * 60) * 3  # 3 hours

# ----------------------------------------------
# Redis settings
REDIS_HOST = 'localhost'  # Redis server hostname
REDIS_PORT = 6379  # Redis server port
REDIS_DB = 0  # Redis database number

# Message expiration time in seconds (e.g., 1 hour = 3600 seconds)
MESSAGE_TTL = (60 * 60) * 3  # 3 hours
# MESSAGE_TTL = 1200  # Adjusted from 3600 to 10 minutes to reduce the window

# Whether to clear Redis message storage on shutdown (default: False)
CLEAR_REDIS_ON_SHUTDOWN = True

# > redis-server    # Start your Redis server
# > redis-cli ping  # Verify Redis is running

# ----------------------------------------------
# Choose how strong the trend must be to confirm a trade
# Options: "Weak", "Moderate", "Strong"
MIN_TREND_STRENGTH = "Strong"
# settings.py
TREND_CONFIG = {
    "Weak": {
        "ADX_THRESHOLD": 20,
        # Lower threshold for trend confirmation. Allows for more frequent but less reliable signals.
        "RSI_PERIOD": 10,  # Shorter RSI period for quicker reaction to price changes but potentially more noise.
        "RSI_OVERSOLD": 35,  # Higher oversold threshold to reduce false buy signals in weak trends.
        "RSI_OVERBOUGHT": 65,  # Lower overbought threshold for the same reason as above.
        "VOLUME_MULTIPLIER": 2.0,
        # Lower volume threshold; less volume needed for confirmation due to expected lower market activity.
        "BREAKOUT_PERCENTAGE": 0.02,
        # 2% breakout threshold; larger move required due to potentially more noise in weak trends.
        "EMA_PERIODS": [7, 21, 50, 100, 200],  # Shorter EMAs for sensitivity to quick market changes.
        "ATR_MULTIPLIER": 1.3
        # Lower ATR multiplier for breakout confirmation to capture smaller, possibly significant moves.
    },
    "Moderate": {
        "ADX_THRESHOLD": 25,  # Standard threshold balancing between frequency and reliability of signals.
        "RSI_PERIOD": 14,  # Default RSI period for balanced sensitivity.
        "RSI_OVERSOLD": 30,
        "RSI_OVERBOUGHT": 70,
        "VOLUME_MULTIPLIER": 2.5,  # Moderate increase in volume requirement for stronger confirmation.
        "BREAKOUT_PERCENTAGE": 0.015,
        # 1.5% breakout; slightly less aggressive than weak trend to account for more stable conditions.
        "EMA_PERIODS": [9, 21, 50, 100, 200],  # Mix of short and long-term EMAs for balanced trend analysis.
        "ATR_MULTIPLIER": 1.5  # Standard ATR multiplier for moderate trends.
    },
    "Strong": {
        "ADX_THRESHOLD": 30,  # Higher threshold for trend confirmation to ensure strong trend signals.
        "RSI_PERIOD": 14,  # Standard RSI period; stability is more valued in strong trends.
        "RSI_OVERSOLD": 25,  # Lower oversold threshold, expecting stronger reversals in strong trends.
        "RSI_OVERBOUGHT": 75,  # Higher overbought threshold for the same reason.
        "VOLUME_MULTIPLIER": 3.0,  # Higher volume requirement for confirmation in line with higher market activity.
        "BREAKOUT_PERCENTAGE": 0.025,  # 2.5% breakout; larger moves expected in strong trends.
        "EMA_PERIODS": [12, 26, 100, 200],  # Longer EMAs for stability and confirmation of strong trends.
        "ATR_MULTIPLIER": 1.7  # Higher ATR multiplier to ensure breakouts are significant in strong trend environments.
    }
}

# ----------------------------------------------
# Backtest
INITIAL_BALANCE = 1000
USE_ALL_SIGNALS_STATUS = False  # Use all_signals_status for decision, else use trade_signal["action"]
BACKTEST_SYMBOL = "BTCUSDT"

# ----------------------------------------------
# CRYPTOs to monitor
# SYMBOLS = ["BNBUSDT", "WLDUSDT", "ALGOUSDT", "PYTHUSDT", "SOLUSDT", "SUIUSDT", "XRPUSDT", "ETHUSDT", "BTCUSDT"]
SYMBOLS = ["BTCUSDT", "WLDUSDT"]  # TEST
