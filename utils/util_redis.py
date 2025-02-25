# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals

import hashlib
import redis
import pickle
import settings

# Import the logger from util_log
from utils.util_log import logger

log = logger()

# Redis connection setup
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=False  # Disable decode_responses to handle binary data (charts)
)


def generate_message_id(full_message, symbol, timestamp):
    """
    Generate a unique identifier for a message using a hash of the message content, symbol, and timestamp.
    This ensures the identifier is unique even if messages for different symbols are identical.

    Parameters:
    - full_message (str): The full message content.
    - symbol (str): The cryptocurrency symbol (e.g., BTCUSDT).
    - timestamp (float): The current timestamp to ensure uniqueness over time.

    Returns:
    - str: A unique message ID (first 8 characters of the MD5 hash for brevity).
    """
    combined = f"{full_message}|{symbol}|{timestamp}"
    message_id = hashlib.md5(combined.encode('utf-8')).hexdigest()[:8]
    log.debug(f"Generated message ID: {message_id} for {symbol} at {timestamp}")
    return message_id


def serialize_statuses(statuses):
    """
    Serialize a dictionary of signal statuses to bytes for storage in Redis.

    Parameters:
    - statuses (dict): Dictionary containing signal statuses (e.g., {"ema_status": "BUY", ...}).

    Returns:
    - bytes: Serialized binary data ready for Redis storage.
    """
    try:
        serialized = pickle.dumps(statuses)
        log.debug(f"Serialized statuses: {statuses}")
        return serialized
    except Exception as e:
        log.error(f"Failed to serialize statuses: {e}")
        raise


def deserialize_statuses(statuses_bytes):
    """
    Deserialize bytes from Redis back into a dictionary of signal statuses.

    Parameters:
    - statuses_bytes (bytes): Binary data retrieved from Redis.

    Returns:
    - dict: Deserialized signal statuses dictionary, or None if deserialization fails.
    """
    try:
        statuses = pickle.loads(statuses_bytes)
        log.debug(f"Deserialized statuses: {statuses}")
        return statuses
    except Exception as e:
        log.error(f"Failed to deserialize statuses: {e}")
        return None


def clear_redis_storage():
    """
    Clear all keys in the current Redis database.
    Used on shutdown if CLEAR_REDIS_ON_SHUTDOWN is True in settings.py.
    """
    try:
        redis_client.flushdb()
        log.info("Cleared all keys in Redis database.")
    except Exception as e:
        log.error(f"Failed to clear Redis database: {e}")


def test_redis_connection():
    """
    Test the Redis connection by setting and retrieving a test value.
    Useful for debugging connection issues.
    """
    try:
        test_key = "test_connection"
        test_value = b"connection_ok"
        redis_client.set(test_key, test_value)
        retrieved = redis_client.get(test_key)
        if retrieved == test_value:
            log.info("Redis connection test successful.")
        else:
            log.error("Redis connection test failed: Retrieved value does not match.")
        redis_client.delete(test_key)  # Clean up
    except Exception as e:
        log.error(f"Redis connection test failed: {e}")


def format_size(bytes_size):
    """
    Convert bytes to a human-readable format (B, KB, MB, etc.).

    Parameters:
    - bytes_size (int): Size in bytes.

    Returns:
    - str: Human-readable size (e.g., "1.23 MB").
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} TB"  # Fallback for very large sizes


def log_redis_size():
    """
    Log the current size of stored messages, charts, and previous statuses in Redis to the console.
    Includes both the number of keys and the total size in bytes (converted to human-readable units).
    Called after each MONITOR_SLEEP interval in main.py.
    """
    try:
        # Count and size messages
        message_keys = redis_client.keys("message:*")
        message_count = len(message_keys)
        message_size = sum(redis_client.memory_usage(key) or 0 for key in message_keys)

        # Count and size charts
        chart_keys = redis_client.keys("chart:*")
        chart_count = len(chart_keys)
        chart_size = sum(redis_client.memory_usage(key) or 0 for key in chart_keys)

        # Count and size previous statuses
        prev_statuses_keys = redis_client.keys("prev_statuses:*")
        prev_statuses_count = len(prev_statuses_keys)
        prev_statuses_size = sum(redis_client.memory_usage(key) or 0 for key in prev_statuses_keys)

        # Total
        total_keys = message_count + chart_count + prev_statuses_count
        total_size = message_size + chart_size + prev_statuses_size

        # Log with counts and sizes
        log.info(
            f"Redis storage size: {total_keys} total keys ({format_size(total_size)}), "
            f"messages: {message_count} ({format_size(message_size)}), "
            f"charts: {chart_count} ({format_size(chart_size)}), "
            f"prev_statuses: {prev_statuses_count} ({format_size(prev_statuses_size)})"
        )
    except Exception as e:
        log.error(f"Failed to retrieve Redis storage size: {e}")
