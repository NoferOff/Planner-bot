from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv
import os

load_dotenv() 
BOT_TOKEN=os.getenv("BOT_TOKEN")


# Title: /start command handler
async def start(update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = ["Welcome to the Planner bot.This is a bot that helps you plan your tasks effectively.!"reply_markup]
# Title: Inline keyboard with options
async def start(update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("➕New Plan",callback_data='new_plan')],
        [InlineKeyboardButton("➕Add Task",callback_data='add_task')],
        [InlineKeyboardButton("🗂 My Tasks",callback_data='my_tasks')],
        [InlineKeyboardButton("⭐ Priorities",callback_data='priorities')],
        [InlineKeyboardButton("📅 Deadlines",callback_data='deadlines')],
        [InlineKeyboardButton("⏰ Reminders",callback_data='reminders')],
        [InlineKeyboardButton("📊 Progress",callback_data='progress')],
        [InlineKeyboardButton("⚙️ Settings",callback_data='settings')]
    ]
    