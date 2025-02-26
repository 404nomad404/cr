import redis
import pickle

# Simulate status change by changing values in redis
# TIP: look into log for this
# Current statuses for BTCUSDT: {'ema_status': 'HOLD', 'rsi_status': 'HOLD', 'sr_status': 'HOLD', 'breakout_status': 'HOLD', 'macd_status': 'SELL', 'wvix_stoch_status': 'HOLD', 'sha_status': 'SELL'}


# Connect to Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=False)

# Simulate a previous state for BTCUSDT
fake_prev_statuses = {
    "ema_status": "HOLD",  # Change this to test different scenarios (SELL, BUY, HOLD)
    "rsi_status": "HOLD",
    "sr_status": "HOLD",
    "breakout_status": "HOLD",
    "macd_status": "SELL",
    "wvix_stoch_status": "BUY",
    "sha_status": "SELL"
}

# Set in Redis
redis_client.set("prev_statuses:BTCUSDT", pickle.dumps(fake_prev_statuses))
print("Simulated prev_statuses for BTCUSDT:", fake_prev_statuses)
