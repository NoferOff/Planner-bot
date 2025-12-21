from telegram import Update,InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv
import os

load_dotenv() 
BOT_TOKEN=os.getenv("BOT_TOKEN")
reply_markup=InlineKeyboardMarkup


# Title: Inline keyboard with options
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard =[
        [InlineKeyboardButton("➕New Plan",callback_data='new_plan')],
        [InlineKeyboardButton("➕Add Task",callback_data='add_task')],
        [InlineKeyboardButton("🗂 My Tasks",callback_data='my_tasks')],
        [InlineKeyboardButton("⭐ Priorities",callback_data='priorities')],
        [InlineKeyboardButton("📅 Deadlines",callback_data='deadlines')],
        [InlineKeyboardButton("⏰ Reminders",callback_data='reminders')],
        [InlineKeyboardButton("📊 Progress",callback_data='progress')],
        [InlineKeyboardButton("⚙️ Settings",callback_data='settings')]
    ]


reply_markup=InlineKeyboardMarkup(keyboard)

await update.effective_message.reply_text("👋 Welcome to the Planner bot!\n\n"
        "This bot helps you plan your tasks effectively.",
        reply_markup=reply_markup
    )

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("Bot is running...")
    app.run_polling()