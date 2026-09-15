# ============ HIDE TOKEN FROM LOGS ============
import logging
logging.getLogger("httpx").setLevel(logging.WARNING)

import os
import random
import asyncio
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("No BOT_TOKEN set!")

# ============ QUIZ QUESTIONS ============
QUESTIONS = [
    {
        "question": "What is the capital of France?",
        "options": ["London", "Berlin", "Paris", "Rome"],
        "answer": "Paris",
        "category": "Geography"
    },
    {
        "question": "How many continents are there on Earth?",
        "options": ["5", "6", "7", "8"],
        "answer": "7",
        "category": "Geography"
    },
    {
        "question": "Which planet is closest to the Sun?",
        "options": ["Venus", "Mercury", "Earth", "Mars"],
        "answer": "Mercury",
        "category": "Science"
    },
    {
        "question": "What is the largest ocean on Earth?",
        "options": ["Atlantic", "Indian", "Arctic", "Pacific"],
        "answer": "Pacific",
        "category": "Geography"
    },
    {
        "question": "Who invented the telephone?",
        "options": ["Thomas Edison", "Alexander Graham Bell", "Nikola Tesla", "Albert Einstein"],
        "answer": "Alexander Graham Bell",
        "category": "History"
    },
    {
        "question": "What is the fastest land animal?",
        "options": ["Lion", "Horse", "Cheetah", "Leopard"],
        "answer": "Cheetah",
        "category": "Nature"
    },
    {
        "question": "How many sides does a hexagon have?",
        "options": ["5", "6", "7", "8"],
        "answer": "6",
        "category": "Math"
    },
    {
        "question": "What is the largest country in the world by area?",
        "options": ["China", "USA", "Canada", "Russia"],
        "answer": "Russia",
        "category": "Geography"
    },
    {
        "question": "Which gas do plants absorb from the atmosphere?",
        "options": ["Oxygen", "Nitrogen", "Carbon Dioxide", "Hydrogen"],
        "answer": "Carbon Dioxide",
        "category": "Science"
    },
    {
        "question": "What year did World War II end?",
        "options": ["1943", "1944", "1945", "1946"],
        "answer": "1945",
        "category": "History"
    },
    {
        "question": "Which is the longest river in the world?",
        "options": ["Amazon", "Nile", "Yangtze", "Mississippi"],
        "answer": "Nile",
        "category": "Geography"
    },
    {
        "question": "What is the chemical symbol for Gold?",
        "options": ["Go", "Gd", "Au", "Ag"],
        "answer": "Au",
        "category": "Science"
    },
    {
        "question": "How many bones are in the adult human body?",
        "options": ["196", "206", "216", "226"],
        "answer": "206",
        "category": "Science"
    },
    {
        "question": "Which country is the largest producer of coffee?",
        "options": ["Colombia", "Ethiopia", "Vietnam", "Brazil"],
        "answer": "Brazil",
        "category": "General"
    },
    {
        "question": "What is the square root of 144?",
        "options": ["10", "11", "12", "13"],
        "answer": "12",
        "category": "Math"
    },
    {
        "question": "Which planet has the most moons?",
        "options": ["Jupiter", "Saturn", "Uranus", "Neptune"],
        "answer": "Saturn",
        "category": "Science"
    },
    {
        "question": "What language is spoken in Brazil?",
        "options": ["Spanish", "Portuguese", "English", "French"],
        "answer": "Portuguese",
        "category": "Geography"
    },
    {
        "question": "Who painted the Mona Lisa?",
        "options": ["Michelangelo", "Raphael", "Leonardo da Vinci", "Picasso"],
        "answer": "Leonardo da Vinci",
        "category": "History"
    },
    {
        "question": "What is the smallest country in the world?",
        "options": ["Monaco", "San Marino", "Vatican City", "Liechtenstein"],
        "answer": "Vatican City",
        "category": "Geography"
    },
    {
        "question": "How many hours are in a week?",
        "options": ["148", "158", "168", "178"],
        "answer": "168",
        "category": "Math"
    },
]

# Store user scores
user_scores = {}
user_current_question = {}

# ============ FLASK - KEEPS HOST ALIVE ============
flask_app = Flask(__name__)

@flask_app.route('/')
def health_check():
    return "Daily Trivia Bot is running!", 200

# ============ HELPERS ============
def get_question(index):
    return QUESTIONS[index % len(QUESTIONS)]

def build_question_keyboard(q_index, options):
    keyboard = []
    for option in options:
        keyboard.append([InlineKeyboardButton(
            option,
            callback_data=f"ans_{q_index}_{option}"
        )])
    return InlineKeyboardMarkup(keyboard)

# ============ COMMANDS ============

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name or "friend"
    user_id = update.effective_user.id
    if user_id not in user_scores:
        user_scores[user_id] = {"correct": 0, "total": 0}

    welcome = (
        f"👋 Hello {user_name}!\n\n"
        "Welcome to <b>Daily Trivia Quiz</b> 🧠\n\n"
        "Test your knowledge with fun trivia questions!\n\n"
        "<b>Commands:</b>\n"
        "/quiz - Start a new question\n"
        "/score - Check your score\n"
        "/help - Show help\n\n"
        "Ready to test your knowledge? Let's go! 🚀"
    )
    await update.message.reply_text(welcome, parse_mode="HTML")

async def quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_scores:
        user_scores[user_id] = {"correct": 0, "total": 0}

    q_index = random.randint(0, len(QUESTIONS) - 1)
    user_current_question[user_id] = q_index
    q = QUESTIONS[q_index]

    options = q["options"].copy()
    random.shuffle(options)

    text = (
        f"🧠 <b>Trivia Question</b>\n"
        f"📂 Category: {q['category']}\n\n"
        f"❓ {q['question']}\n\n"
        "Choose your answer 👇"
    )

    await update.message.reply_text(
        text,
        parse_mode="HTML",
        reply_markup=build_question_keyboard(q_index, options)
    )

async def score_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_scores:
        user_scores[user_id] = {"correct": 0, "total": 0}

    score = user_scores[user_id]
    correct = score["correct"]
    total = score["total"]
    percentage = int((correct / total) * 100) if total > 0 else 0

    if percentage >= 80:
        grade = "🏆 Excellent!"
    elif percentage >= 60:
        grade = "👍 Good!"
    elif percentage >= 40:
        grade = "📚 Keep learning!"
    else:
        grade = "💪 Keep trying!"

    text = (
        "📊 <b>Your Score</b>\n\n"
        f"✅ Correct: {correct}\n"
        f"❌ Wrong: {total - correct}\n"
        f"📝 Total: {total}\n"
        f"📈 Accuracy: {percentage}%\n\n"
        f"{grade}\n\n"
        "Use /quiz to answer more questions!"
    )
    await update.message.reply_text(text, parse_mode="HTML")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🧠 <b>Daily Trivia Quiz Bot</b>\n\n"
        "Test your knowledge every day!\n\n"
        "<b>Commands:</b>\n"
        "/start - Welcome message\n"
        "/quiz - Get a new question\n"
        "/score - Check your score\n"
        "/help - Show this help\n\n"
        "<b>Categories:</b>\n"
        "🌍 Geography\n"
        "🔬 Science\n"
        "📜 History\n"
        "🌿 Nature\n"
        "🔢 Math\n"
        "🌐 General Knowledge\n\n"
        "Keep playing and improve your score! 🏆"
    )
    await update.message.reply_text(help_text, parse_mode="HTML")

# ============ CALLBACK HANDLER ============

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    data = query.data

    if data.startswith("ans_"):
        parts = data.split("_", 2)
        q_index = int(parts[1])
        selected = parts[2]

        q = QUESTIONS[q_index]
        correct_answer = q["answer"]

        if user_id not in user_scores:
            user_scores[user_id] = {"correct": 0, "total": 0}

        user_scores[user_id]["total"] += 1

        if selected == correct_answer:
            user_scores[user_id]["correct"] += 1
            result = (
                f"✅ <b>Correct!</b>\n\n"
                f"The answer is: <b>{correct_answer}</b>\n\n"
                f"🏆 Score: {user_scores[user_id]['correct']}/{user_scores[user_id]['total']}\n\n"
                "Use /quiz for the next question!"
            )
        else:
            result = (
                f"❌ <b>Wrong!</b>\n\n"
                f"Your answer: {selected}\n"
                f"Correct answer: <b>{correct_answer}</b>\n\n"
                f"📊 Score: {user_scores[user_id]['correct']}/{user_scores[user_id]['total']}\n\n"
                "Use /quiz to try another question!"
            )

        await query.edit_message_text(result, parse_mode="HTML")

    elif data == "next":
        q_index = random.randint(0, len(QUESTIONS) - 1)
        user_current_question[user_id] = q_index
        q = QUESTIONS[q_index]
        options = q["options"].copy()
        random.shuffle(options)

        text = (
            f"🧠 <b>Trivia Question</b>\n"
            f"📂 Category: {q['category']}\n\n"
            f"❓ {q['question']}\n\n"
            "Choose your answer 👇"
        )
        await query.edit_message_text(
            text,
            parse_mode="HTML",
            reply_markup=build_question_keyboard(q_index, options)
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")

# ============ BOT STARTUP ============
async def run_bot_async():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("quiz", quiz_command))
    app.add_handler(CommandHandler("score", score_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_error_handler(error_handler)

    await app.initialize()
    await app.start()
    await app.updater.start_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True
    )
    logger.info("Daily Trivia Quiz Bot is polling and ready!")
    while True:
        await asyncio.sleep(1)

def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_bot_async())

bot_thread = threading.Thread(target=run_bot, daemon=True)
bot_thread.start()
