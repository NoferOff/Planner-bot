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
import os
import asyncio

# ---------- ENV ----------
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ---------- STORAGE ----------
tasks = {}          # user_id -> list of tasks
user_state = {}     # user_id -> state
temp_data = {}      # user_id -> temp values (priority, reminders)

# ---------- KEYBOARD ----------
def get_keyboard():
    return InlineKeyboardMarkup([
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
        "👋 Welcome to the Planner bot!\n\nChoose an action:",
        reply_markup=get_keyboard()
    )

# ---------- BUTTON HANDLER ----------
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data

    tasks.setdefault(user_id, [])
    await query.answer()

    # ➕ NEW PLAN
    if data == "new_plan":
        tasks[user_id] = []
        await query.message.edit_text(
            "🧹 New plan created. All tasks cleared.",
            reply_markup=get_keyboard()
        )

    # ➕ ADD TASK
    elif data == "add_task":
        user_state[user_id] = "WAIT_TASK"
        await query.message.edit_text(
            "✏️ Send the task text:",
            reply_markup=get_keyboard()
        )

    # 🗂 MY TASKS
    elif data == "my_tasks":
        if not tasks[user_id]:
            await query.message.edit_text(
                "🗂 You have no tasks yet.",
                reply_markup=get_keyboard()
            )
        else:
            text = "🗂 Your tasks:\n\n"
            for i, t in enumerate(tasks[user_id], 1):
                text += f"{i}. {t['text']} | {t['priority']}\n"
            await query.message.edit_text(text, reply_markup=get_keyboard())

    # ⭐ PRIORITIES
    elif data == "priorities":
        if not tasks[user_id]:
            await query.message.edit_text(
                "⭐ No tasks to prioritize.",
                reply_markup=get_keyboard()
            )
        else:
            buttons = []
            text = "⭐ Choose a task:\n\n"
            for i, t in enumerate(tasks[user_id], 1):
                text += f"{i}. {t['text']} ({t['priority']}) ({t['deadline']})\n"
                buttons.append(
                    [InlineKeyboardButton(str(i), callback_data=f"pick_task_{i}")]
                )
            await query.message.edit_text(
                text,
                reply_markup=InlineKeyboardMarkup(buttons)
            )

    # 📅 DEADLINES
    elif data == "deadlines":
        if not tasks[user_id]:
            await query.message.edit_text(
                "🗂You have no tasks",
                reply_markup=get_keyboard()
            )
        else:
            buttons - []
            text = "Write a deadline📅\n\n"
            for i,t in enumerate(tasks[user_id], 1):
                 text += f"{i}. {t['text']} ({t['priority']}) ({t['deadline']})\n"
                 buttons.append(
                    [InlineKeyboardButton(str(i), callback_data=f"pick_task_{i}")]
                )
            await query.message.edit_text(
                text,
                reply_markup=InlineKeyboardMarkup(buttons)
            )

    # ⏰ REMINDERS
    elif data == "reminders":
        user_state[user_id] = "WAIT_REMINDER_TEXT"
        await query.message.edit_text(
            "⏰ What should I remind you about?",
            reply_markup=get_keyboard()
        )

    # 📊 PROGRESS
    elif data == "progress":
        total = len(tasks[user_id])
        await query.message.edit_text(
            f"📊 Progress:\nTotal tasks: {total}",
            reply_markup=get_keyboard()
        )

    # ⚙️ SETTINGS
    elif data == "settings":
        await query.message.edit_text(
            "⚙️ Settings will be available later.",
            reply_markup=get_keyboard()
        )

    # ---------- PRIORITY FLOW ----------
    elif data.startswith("pick_task_"):
        index = int(data.split("_")[-1]) - 1
        temp_data[user_id] = index

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🟢 Low", callback_data="set_low")],
            [InlineKeyboardButton("🟡 Medium", callback_data="set_medium")],
            [InlineKeyboardButton("🔴 High", callback_data="set_high")]
        ])

        await query.message.edit_text(
            "⭐ Choose priority:",
            reply_markup=keyboard
        )

    elif data.startswith("set_"):
        priority = data.replace("set_", "") 
        index = temp_data.get(user_id)

        if index is not None:
            tasks[user_id][index]["priority"] = priority

        temp_data.pop(user_id, None)

        await query.message.edit_text(
            f"✅ Priority set to {priority}.",
            reply_markup=get_keyboard()
        )


    elif data.startswith("pick_task_"):
        index =int(data.spilt("_")[-1]) -1
       temp_data[user_id] = index

      

# ---------- TEXT HANDLER ----------
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text
    state = user_state.get(user_id)

    # ADD TASK TEXT
    if state == "WAIT_TASK":
        tasks[user_id].append({
            "text": text,
            "priority": None,
            "deadline": None
        })
        user_state.pop(user_id)
        await update.message.reply_text(
            "✅ Task added.",
            reply_markup=get_keyboard()
        )

    # REMINDER TEXT
    elif state == "WAIT_REMINDER_TEXT":
        temp_data[user_id] = text
        user_state[user_id] = "WAIT_REMINDER_TIME"
        await update.message.reply_text("⏱ In how many minutes?")

    # REMINDER TIME
    elif state == "WAIT_REMINDER_TIME":
        if not text.isdigit():
            await update.message.reply_text("❌ Enter a number.")
            return

        minutes = int(text)
        reminder = temp_data[user_id]
        user_state.pop(user_id)
        temp_data.pop(user_id)

        await update.message.reply_text(
            f"✅ Reminder set for {minutes} minutes."
        )

        await asyncio.sleep(minutes * 60)

        await update.message.reply_text(
            f"⏰ Reminder:\n{reminder}",
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
