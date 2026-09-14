# ============ HIDE TOKEN FROM LOGS ============
import logging
logging.getLogger("httpx").setLevel(logging.WARNING)

import os
import json
import random
import asyncio
import threading
import datetime
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("No BOT_TOKEN set!")

# ============ LOAD WORDS ============
def load_words():
    try:
        with open("words.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading words.json: {e}")
        return []

WORDS = load_words()
logger.info(f"Loaded {len(WORDS)} words.")

# ============ FORMAT WORD ============
def format_word(word_data):
    return (
        f"📖 <b>{word_data['word']}</b>\n"
        f"🔊 <i>{word_data.get('pronunciation', '')}</i>\n"
        f"📝 Type: <i>{word_data.get('type', 'N/A')}</i>\n\n"
        f"💡 <b>Meaning:</b>\n{word_data.get('meaning', '')}\n\n"
        f"✏️ <b>Example:</b>\n<i>{word_data.get('example', '')}</i>"
    )

# ============ FLASK - KEEPS HOST ALIVE ============
flask_app = Flask(__name__)

@flask_app.route('/')
def health_check():
    return "Daily English Words Bot is running!", 200

# ============ COMMANDS ============

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name or "friend"
    welcome = (
        f"👋 Hello {user_name}!\n\n"
        "Welcome to <b>Daily English Words</b> 📚\n\n"
        "I teach you a new English word every day "
        "with meaning, pronunciation, and an example.\n\n"
        "<b>Commands:</b>\n"
        "/word - Get today's word\n"
        "/random - Get a random word\n"
        "/help - Show help\n\n"
        "Here's your word of the day 👇"
    )
    await update.message.reply_text(welcome, parse_mode="HTML")
    today_index = datetime.date.today().toordinal() % len(WORDS)
    word = WORDS[today_index]
    await update.message.reply_text(format_word(word), parse_mode="HTML")

async def word_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today_index = datetime.date.today().toordinal() % len(WORDS)
    word = WORDS[today_index]
    await update.message.reply_text(format_word(word), parse_mode="HTML")

async def random_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    word = random.choice(WORDS)
    await update.message.reply_text(format_word(word), parse_mode="HTML")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📚 <b>Daily English Words Bot</b>\n\n"
        "Learn new English words every day!\n\n"
        "<b>Commands:</b>\n"
        "/start - Welcome and today's word\n"
        "/word - Get today's word\n"
        "/random - Get a random word\n"
        "/help - Show this help\n\n"
        "Keep learning and improving! 💪"
    )
    await update.message.reply_text(help_text, parse_mode="HTML")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")

# ============ BOT STARTUP ============
async def run_bot_async():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("word", word_command))
    app.add_handler(CommandHandler("random", random_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_error_handler(error_handler)

    await app.initialize()
    await app.start()
    await app.updater.start_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True
    )
    logger.info("Daily English Words Bot is polling and ready!")
    while True:
        await asyncio.sleep(1)

def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_bot_async())

bot_thread = threading.Thread(target=run_bot, daemon=True)
bot_thread.start()
