from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv
import os

load_dotenv() 
BOT_TOKEN=os.getenv("BOT_TOKEN")


# Title: /start command handler
async def start(update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = ["Hello.This is a bot that helps you plan your tasks effectively.!"]