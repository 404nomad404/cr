import redis
import pickle

# Connect to Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=False)

# Simulate a previous state for BTCUSDT with ema_status as SELL
fake_prev_statuses = {
    "ema_status": "BUY",  # Change this to test different scenarios (SELL, BUY, HOLD)
    "rsi_status": "HOLD",
    "sr_status": "HOLD",
    "breakout_status": "HOLD",
    "macd_status": "HOLD"
}

# Set in Redis
redis_client.set("prev_statuses:BTCUSDT", pickle.dumps(fake_prev_statuses))
print("Simulated prev_statuses for BTCUSDT:", fake_prev_statuses)
