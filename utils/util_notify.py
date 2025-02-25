# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals

__author__ = 'Ishafizan'
__date__ = "15 Feb 2025"

import settings
import telegram
import asyncio
import random
from telegram import InlineKeyboardMarkup
from utils import util_chart, util_log

# Import logger
log = util_log.logger()

TELEGRAM_CHAT_ID = settings.TELEGRAM_CHAT_ID
BOT_USERNAME = settings.BOT_USERNAME
bot = telegram.Bot(token=settings.TELEGRAM_BOT_TOKEN)

async def handle_read_more(update, context):
    """
    Callback function to handle the "Read More" button click.
    Sends the full detailed analysis as a text message and the chart separately to the user privately,
    with a confirmation in the group chat.
    """
    query = update.callback_query
    await query.answer()  # Acknowledge the callback query

    log.info(f"Callback query received: {query.from_user}")

    # Extract the message ID from callback_data
    try:
        message_id = query.data.split("|", 1)[1]
    except IndexError:
        log.error(f"Invalid callback_data format: {query.data}")
        await context.bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text="⚠️ An error occurred while processing your request. Please try again later.",
            parse_mode="Markdown",
            reply_to_message_id=query.message.message_id
        )
        return

    try:
        # Retrieve the full message from Redis
        full_message = context.bot_data['redis_client'].get(f"message:{message_id}")
        if full_message:
            full_message = full_message.decode('utf-8')  # Decode binary data to string
            # Retrieve the chart image from Redis
            chart_image = context.bot_data['redis_client'].get(f"chart:{message_id}")
            if chart_image is None:
                log.warning(f"Chart image not found in Redis for message_id: {message_id}")
                chart_image = None

            log.info(f"Retrieved full message from Redis for message_id: {message_id}")
            user_id = query.from_user.id

            try:
                # Send the full analysis as a text message (up to 4096 characters)
                await context.bot.send_message(
                    chat_id=user_id,
                    text=full_message,
                    parse_mode="Markdown"
                )
                # Send the chart with a short caption if available
                if chart_image:
                    short_caption = f"Chart for {symbol_from_message_id(message_id)}"
                    await context.bot.send_photo(
                        chat_id=user_id,
                        photo=chart_image,
                        caption=short_caption,
                        parse_mode="Markdown"
                    )
                log.info(f"Successfully sent full analysis and chart to user {user_id} for message_id: {message_id}")

                # Inform the user in the group chat
                await context.bot.send_message(
                    chat_id=TELEGRAM_CHAT_ID,
                    text=f"📩 The chart & detailed analysis have been sent to your private chat with {BOT_USERNAME}. Start [Private Chat](https://t.me/{BOT_USERNAME}?start=init) if you haven't already.",
                    parse_mode="Markdown",
                    reply_to_message_id=query.message.message_id
                )
            except Exception as private_msg_error:
                log.error(f"Failed to send private message to user {user_id}: {private_msg_error}")
                await context.bot.send_message(
                    chat_id=TELEGRAM_CHAT_ID,
                    text="⚠️ Unable to send the detailed analysis privately. Please ensure you’ve started a private chat with the bot.",
                    parse_mode="Markdown",
                    reply_to_message_id=query.message.message_id
                )
        else:
            await context.bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text="⚠️ Sorry, the detailed analysis is no longer available. Please wait for the next alert.",
                parse_mode="Markdown",
                reply_to_message_id=query.message.message_id
            )
            log.warning(f"Full message not found in Redis for message_id: {message_id}")

    except Exception as e:
        log.error(f"Failed to process read more request: {e}")
        await context.bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text="⚠️ An error occurred while retrieving the detailed analysis. Please try again later.",
            parse_mode="Markdown",
            reply_to_message_id=query.message.message_id
        )

def symbol_from_message_id(message_id):
    """
    Extract the symbol from the message_id (assumes format like 'BTCUSDT_timestamp').
    """
    return message_id.split('_')[0]  # Adjust based on your actual message_id format

async def send_telegram_alert_with_chart(log, message, df, symbol, reply_markup=None):
    """
    Send a Telegram alert with a chart and an optional inline button.

    Parameters:
    - log: Logger instance for logging.
    - message (str): The message text to send (short summary or full analysis).
    - df (DataFrame): DataFrame containing price data for chart generation.
    - symbol (str): The cryptocurrency symbol (e.g., BTCUSDT).
    - reply_markup (InlineKeyboardMarkup, optional): Inline keyboard markup for buttons.
    """
    try:
        # Generate the price chart image
        img = util_chart.generate_price_chart(df, symbol)

        # Add a random delay to avoid rate limiting
        await asyncio.sleep(random.uniform(1, 3))

        # Send the message with the chart and optional inline button
        if reply_markup:
            await bot.send_photo(
                chat_id=TELEGRAM_CHAT_ID,
                photo=img,
                caption=message,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
        else:
            await bot.send_photo(
                chat_id=TELEGRAM_CHAT_ID,
                photo=img,
                caption=message,
                parse_mode="Markdown"
            )
        log.info(f"Successfully sent Telegram message with chart for {symbol}")
        log.info("*" * 40)

    except Exception as e:
        log.error(f"Failed to send Telegram message with chart for {symbol}: {e}")

async def send_alert_async_with_chart(log, message, df, symbol, reply_markup=None):
    """
    Asynchronous wrapper for sending alerts with charts.

    Parameters:
    - log: Logger instance for logging.
    - message (str): The message text to send (short summary or full analysis).
    - df (DataFrame): DataFrame containing price data for chart generation.
    - symbol (str): The cryptocurrency symbol (e.g., BTCUSDT).
    - reply_markup (InlineKeyboardMarkup, optional): Inline keyboard markup for buttons.
    """
    await send_telegram_alert_with_chart(log, message, df, symbol, reply_markup)
