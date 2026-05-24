# main.py
from config import API_TOKEN
import telebot

# Import handlers
from handlers.onboarding import register_onboarding_handlers
from handlers.weight_flow import register_weight_handlers
from handlers.common import register_common_handlers

# Import Database Setup
from db.operations import init_db

# Ensure all structural storage engines exist on system start
init_db()

# Initialize Bot
bot = telebot.TeleBot(API_TOKEN)

# Register Handlers
register_onboarding_handlers(bot)
register_weight_handlers(bot)
register_common_handlers(bot)

if __name__ == "__main__":
    print("🤖 Weight Tracker Bot is running smoothly with Live Database routing...")
    bot.polling(none_stop=True, timeout=60)

    '''
    What these parameters do:
timeout=60: Extends the time the requests library is allowed to wait for Telegram's server to answer before giving up.

none_stop=True: Tells the library that if a connection does timeout or drop entirely, it should immediately catch the error under the hood, recreate the session, and continue polling without crashing your terminal script.
    '''