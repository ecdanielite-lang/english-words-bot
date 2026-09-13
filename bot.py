import os
import json
import random
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ==================== LOAD CONFIGURATION ====================
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN not found in .env file!")

# ==================== LOAD WORDS ====================
def load_words():
    """Load words from words.json"""
    try:
        with open("words.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading words.json: {e}")
        return []

WORDS = load_words()
print(f"📚 Loaded {len(WORDS)} words.")

# ==================== FORMAT WORD MESSAGE ====================
def format_word(word_data):
    """Format a word into a nice message."""
    return (
        f"📖 *{word_data['word']}*\n"
        f"🔊 _{word_data.get('pronunciation', '')}_\n"
        f"📝 Type: _{word_data.get('type', 'N/A')}_\n\n"
        f"💡 *Meaning:*\n{word_data.get('meaning', '')}\n\n"
        f"✏️ *Example:*\n_{word_data.get('example', '')}_"
    )

# ==================== COMMAND HANDLERS ====================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message + the word of the day."""
    user_name = update.effective_user.first_name or "friend"
    
    welcome = (
        f"👋 Hello {user_name}!\n\n"
        f"Welcome to *Daily English Words* 📚\n\n"
        f"I'll teach you a new English word every day "
        f"with meaning, pronunciation, and an example.\n\n"
        f"*Commands:*\n"
        f"/word – Get today's word\n"
        f"/random – Get a random word\n"
        f"/help – Show this help\n\n"
        f"Here's your word of the day 👇"
    )
    await update.message.reply_text(welcome, parse_mode="Markdown")
    
    # Send the word of the day (deterministic based on date)
    import datetime
    today_index = datetime.date.today().toordinal() % len(WORDS)
    word = WORDS[today_index]
    await update.message.reply_text(format_word(word), parse_mode="Markdown")

async def word_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send today's word."""
    import datetime
    today_index = datetime.date.today().toordinal() % len(WORDS)
    word = WORDS[today_index]
    await update.message.reply_text(format_word(word), parse_mode="Markdown")

async def random_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a random word."""
    word = random.choice(WORDS)
    await update.message.reply_text(format_word(word), parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help."""
    help_text = (
        "📚 *Daily English Words Bot*\n\n"
        "I help you learn new English words every day!\n\n"
        "*Available commands:*\n"
        "/start – Welcome + today's word\n"
        "/word – Get today's word\n"
        "/random – Get a random word\n"
        "/help – Show this help\n\n"
        "Keep learning and improving! 💪"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

# ==================== MAIN ====================
def main():
    """Start the bot."""
    print("🚀 Starting Daily English Words Bot...")
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Register command handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("word", word_command))
    app.add_handler(CommandHandler("random", random_command))
    app.add_handler(CommandHandler("help", help_command))
    
    print("✅ Bot is running! Press Ctrl+C to stop.")
    app.run_polling()

if __name__ == "__main__":
    main()
