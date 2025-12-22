from telegram import Update,InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler,CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv
import os

load_dotenv() 
BOT_TOKEN=os.getenv("BOT_TOKEN")


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
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query=update.callback_query
    data=query.data
    await query.answer()

    if query.data == 'new_plan':
        await query.message.reply_text(
            "Let's create a new plan step by step.\n"
            "You can organize your goals and tasks clearly."
        )
    elif query.data == 'add_task':
        await query.message.reply_text(
            "Please enter the task you want to add to your plan."
        )
    elif query.data == 'my_tasks':
        await query.message.reply_text(
            "Here is a list of all your current tasks."
        )
    elif query.data == 'priorities':
        await query.message.reply_text(
            "Set and manage task priorities to focus on what matters most."
        )
    elif query.data == 'deadlines':
        await query.message.reply_text(
            "View and manage deadlines for your tasks."
        )
    elif query.data =='reminders':
        await query.message.reply_text(
            "Manage reminders so you never forget an important task."
        )
    elif query.data == 'progress':
        await query.message.reply_text(
            "Track your productivity and see how much you’ve accomplished."
        )
    elif query.data == 'settings':
        await query.message.reply_text(
            "Customize your planner and adjust bot preferences."
        )


if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("Bot is running...")
    app.run_polling()