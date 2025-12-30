from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters

)
from dotenv import load_dotenv
import os,asyncio

# ---------- ENV ----------
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ---------- STORAGE ----------
last_message = {}
reminders = {}
tasks = {}        # user_id -> list of tasks
user_state = {}   # user_id -> current state


# ---------- KEYBOARD ----------
def get_keyboard():
    return InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("➕ New Plan", callback_data="new_plan")],
        [InlineKeyboardButton("➕ Add Task", callback_data="add_task")],
        [InlineKeyboardButton("🗂 My Tasks", callback_data="my_tasks")],
        [InlineKeyboardButton("⭐ Priorities", callback_data="priorities")],
        [InlineKeyboardButton("📅 Deadlines", callback_data="deadlines")],
        [InlineKeyboardButton("⏰ Reminders", callback_data="reminders")],
        [InlineKeyboardButton("📊 Progress", callback_data="progress")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="settings")]
    ])
    


# ---------- /start ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to the Planner bot!\n\n"
        "Use the buttons below to manage your tasks.",
        reply_markup=get_keyboard()
    )


# ---------- BUTTON HANDLER ----------
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data

    if user_id in last_message:
        try:
         await context.bot.delete_message(chat_id=query.message.chat_id,
                                         message_id=last_message[user_id]) 
        except:
          pass
   
    tasks.setdefault(user_id, [])

    await query.answer()

    if data == "new_plan":
        await query.message.edit_text(
            "📝 New plan started.\nAdd tasks to begin.",
            reply_markup=get_keyboard()
        )

    elif data == "add_task":
        user_state[user_id] = "WAIT_TASK"
        await query.message.edit_text(
            "✏️ Send the task text:",
            reply_markup=get_keyboard()
        )

    elif data == "my_tasks":
        if not tasks[user_id]:
            await query.message.edit_text(
                "🗂 You have no tasks yet.",
                reply_markup=get_keyboard()
            )
        else:
            text = "🗂 Your tasks:\n"
            for i, t in enumerate(tasks[user_id], 1):
                text += f"{i}. {t['text']}\n"

            await query.message.edit_text(
                text,
                reply_markup=get_keyboard()
            )

    elif data == "priorities":
        if not tasks[user_id]:
            await query.message.edit_text(
                "⭐ No tasks to prioritize.",
                reply_markup=get_keyboard()
            )
        else:
            text = "⭐ Tasks (priorities not set yet):\n"
            for i, t in enumerate(tasks[user_id], 1):
                text += f"{i}. {t['text']}\n"

    elif data == "deadlines":
        if not tasks[user_id]:
           await query.message.edit_text(
            "📅 No tasks with deadlines.",
            reply_markup=get_keyboard()
        )
        else:
            text = "⭐ Tasks (deadlines not set yet):\n"
            for i, t in enumerate(tasks[user_id], 1):
               text == f"{i}. {t["text"]}\n"

    elif data == "reminders":
       user_state[user_id] = "WAIT_REMINDERS_TEXT"
       await query.message.edit_text(
           "What should I remind you about"
       )
      

    elif data == "progress":
        await query.message.edit_text(
            f"📊 Total tasks: {len(tasks[user_id])}",
            reply_markup=get_keyboard()
        )

    elif data == "settings":
        await query.message.edit_text(
            "⚙️ Settings will be available later.",
            reply_markup=get_keyboard()
        )


# ---------- TEXT HANDLER ----------
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    if user_state.get(user_id) == "WAIT_TASK":
        tasks.setdefault(user_id, []).append({
            "text": text,
            "priority": None,
            "deadline": None
        })

        user_state.pop(user_id)

        await update.message.reply_text(
            "✅ Task added!\nPress ➕ Add Task to add another.",
            reply_markup=get_keyboard()
        )


# ---------- MAIN ----------
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    print("🤖 Bot is running...")
    app.run_polling()
