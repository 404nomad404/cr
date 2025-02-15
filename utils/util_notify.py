# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

__author__ = 'Ishafizan'
__date__: "15 Feb 2025"

import settings
import telegram
import asyncio
import random
from utils import util_chart

TELEGRAM_CHAT_ID = settings.TELEGRAM_CHAT_ID
bot = telegram.Bot(token=settings.TELEGRAM_BOT_TOKEN)


async def send_telegram_alert_with_chart(log, message, df, symbol):
    """ Send Telegram alert with chart"""
    try:
        img = util_chart.generate_price_chart(df, symbol)
        # Ensure the image is completely written before sending
        await asyncio.sleep(random.uniform(1, 3))  # Add random delay. asyncio.sleep to avoid blocking
        await bot.send_photo(chat_id=TELEGRAM_CHAT_ID, photo=img, caption=message, parse_mode="Markdown")
    except Exception as e:
        log.error(f"Failed to send Telegram message with chart for {symbol}: {e}\n {message}")


def send_alert_sync_with_chart(log, message, df, symbol):
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    loop.run_until_complete(send_telegram_alert_with_chart(log, message, df, symbol))
