from telegram import Update,InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler,CallbackQueryHandler, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv
import os

load_dotenv() 
BOT_TOKEN=os.getenv("BOT_TOKEN")

tasks ={}
user_state ={}


# Title: Inline keyboard with options
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard =[
        [InlineKeyboardButton("➕ New Plan",callback_data='new_plan')],
        [InlineKeyboardButton("➕ Add Task",callback_data='add_task')],
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
    await query.answer()

    user_id = query.from_user.id
    data=query.data

    tasks.setdefault(user_id, [])


    if query.data == 'new_plan':
        tasks[user_id] = "WAIT_TASK"
        await query.message.reply_text(
            "Let's create a new plan step by step.\n"
            "You can organize your goals and tasks clearly."
        )
    elif query.data == 'add_task':
        tasks[user_id] = []
        await query.message.reply_text(
            "Please enter the task you want to add to your plan."
        )

    elif query.data == 'my_tasks':
        if not tasks[user_id]:
            await query.message.reply_text(
            "No tasks yet."
        )
        else:
            text = "🗂 Your tasks:\n"
            for i,t in enumerate(tasks[user_id], 1):
                text += f"{i}. {t['text']}"
                await query.message.reply_text(text)
        
    elif query.data == 'priorities':
        if not tasks[user_id]:
            await query.message.reply_text(
                "Add the tasks!"
            )
        else:
         user_state[user_id] = "WAIT_PRIORITY"
         await query.message.reply_text("⭐ Send priority (Low / Medium / High).")
        
    elif query.data == 'deadlines':
        if not tasks[user_id]:
            await query.message.reply_text("You have no tasks yet")
        else:
         user_state[user_id] = "WAIT_DEADLINES"
         await query.message.reply_text("📅 Send deadline (e.g. 2025-03-10).")
         
    elif query.data =='reminders':
        await query.message.reply_text(
            "Manage reminders so you never forget an important task."
        )
    elif query.data == 'progress':
        total = len(tasks[user_id])
        await query.message.reply_text(
            f"📊 Progress\nTotal tasks: {total}"
        )
    elif query.data == 'settings':
        await query.message.reply_text(
            "⚙️ Settings\nLanguage: EN\nNotifications: ON"
        )




async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
 user_id = update.message.from_user.id
 text = update.message.text

 if user_state.get(user_id) == "WAIT_TASK":
    tasks[user_id].append({"text": text, "priority": None, "deadline": None})
    user_state.pop(user_id)
    await update.message.reply_text("✅ Task added.")

 if user_state.get(user_id) == "WAIT_PRIORITY":
    tasks[user_id][-1]["priority"] = text
    user_state.pop(user_id)
    await update.message.reply_text(f"⭐ Priority set: {text}")
     
 if user_state.get(user_id) == "WAIT_DEADLINES":
    tasks[user_id][-1]["deadlines"] = text
    user_


if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT))
    print("Bot is running...")
    app.run_polling()