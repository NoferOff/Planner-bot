import os
import asyncio
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ---------- ENV ----------
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ---------- STORAGE ----------
tasks = {}          # user_id -> list of tasks
user_state = {}     # user_id -> state
temp_data = {}      # user_id -> temp values (task index, reminder text)

# ---------- KEYBOARDS ----------
def get_main_keyboard():
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

# ---------- /START ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to the Planner bot!\n\nChoose an action:",
        reply_markup=get_main_keyboard()
    )

# ---------- BUTTON HANDLER ----------
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data

    tasks.setdefault(user_id, [])
    await query.answer()

    # 1. NEW PLAN
    if data == "new_plan":
        tasks[user_id] = []
        await query.message.edit_text("🧹 New plan created. All tasks cleared.", reply_markup=get_main_keyboard())

    # 2. ADD TASK
    elif data == "add_task":
        user_state[user_id] = "WAIT_TASK"
        await query.message.edit_text("✏️ Send the task text:", reply_markup=None)

    # 3. MY TASKS
    elif data == "my_tasks":
        if not tasks[user_id]:
            await query.message.edit_text("🗂 You have no tasks yet.", reply_markup=get_main_keyboard())
        else:
            text = "🗂 Your tasks:\n\n"
            for i, t in enumerate(tasks[user_id], 1):
                text += f"{i}. {t['text']} | Priority: {t['priority']} | Deadline: {t['deadline']}\n"
            await query.message.edit_text(text, reply_markup=get_main_keyboard())

    # 4. PRIORITIES (Show list to pick)
    elif data == "priorities":
        if not tasks[user_id]:
            await query.message.edit_text("⭐ No tasks to prioritize.", reply_markup=get_main_keyboard())
        else:
            buttons = [[InlineKeyboardButton(f"{i+1}. {t['text']}", callback_data=f"pick_pri_{i}")] for i, t in enumerate(tasks[user_id])]
            await query.message.edit_text("⭐ Choose a task to set priority:", reply_markup=InlineKeyboardMarkup(buttons))

    # 5. DEADLINES (Show list to pick)
    elif data == "deadlines":
        if not tasks[user_id]:
            await query.message.edit_text("📅 No tasks to set deadlines.", reply_markup=get_main_keyboard())
        else:
            buttons = [[InlineKeyboardButton(f"{i+1}. {t['text']}", callback_data=f"pick_dead_{i}")] for i, t in enumerate(tasks[user_id])]
            await query.message.edit_text("📅 Choose a task to set deadline:", reply_markup=InlineKeyboardMarkup(buttons))

    # 6. REMINDERS
    elif data == "reminders":
        user_state[user_id] = "WAIT_REMINDER_TEXT"
        await query.message.edit_text("⏰ What should I remind you about?", reply_markup=None)

    # 7. PROGRESS
    elif data == "progress":
        total = len(tasks[user_id])
        completed = sum(1 for t in tasks[user_id] if t['priority'] == "Done") # Example logic
        await query.message.edit_text(f"📊 Progress:\nTotal tasks: {total}", reply_markup=get_main_keyboard())

    # 8. SETTINGS
    elif data == "settings":
        await query.message.edit_text("⚙️ Settings will be available later.", reply_markup=get_main_keyboard())

    # --- SUB-HANDLERS ---
    
    # Priority Selection
    elif data.startswith("pick_pri_"):
        temp_data[user_id] = int(data.split("_")[-1])
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🟢 Low", callback_data="set_Low")],
            [InlineKeyboardButton("🟡 Medium", callback_data="set_Medium")],
            [InlineKeyboardButton("🔴 High", callback_data="set_High")]
        ])
        await query.message.edit_text("Choose priority level:", reply_markup=keyboard)

    elif data.startswith("set_"):
        prio = data.split("_")[-1]
        idx = temp_data.get(user_id)
        if idx is not None:
            tasks[user_id][idx]["priority"] = prio
        user_state.pop(user_id, None)
        await query.message.edit_text(f"✅ Priority set to {prio}!", reply_markup=get_main_keyboard())

    # Deadline Selection
    elif data.startswith("pick_dead_"):
        temp_data[user_id] = int(data.split("_")[-1])
        user_state[user_id] = "WAIT_DEADLINE_INPUT"
        await query.message.edit_text("📅 Type the deadline (e.g., '12:00' or 'Monday'):", reply_markup=None)

# ---------- TEXT HANDLER ----------
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text
    state = user_state.get(user_id)

    # State: Adding new task text
    if state == "WAIT_TASK":
        tasks[user_id].append({"text": text, "priority": "None", "deadline": "None"})
        user_state.pop(user_id, None)
        await update.message.reply_text(f"✅ Task '{text}' added!", reply_markup=get_main_keyboard())

    # State: Setting deadline text
    elif state == "WAIT_DEADLINE_INPUT":
        idx = temp_data.get(user_id)
        if idx is not None:
            tasks[user_id][idx]["deadline"] = text
            user_state.pop(user_id, None)
            temp_data.pop(user_id, None)
            await update.message.reply_text(f"✅ Deadline '{text}' saved!", reply_markup=get_main_keyboard())

    # State: Reminder text
    elif state == "WAIT_REMINDER_TEXT":
        temp_data[user_id] = text
        user_state[user_id] = "WAIT_REMINDER_TIME"
        await update.message.reply_text("⏱ In how many minutes?")

       # State: Reminder time
    elif state == "WAIT_REMINDER_TIME":
        if not text.isdigit():
            await update.message.reply_text("❌ Please enter a number (minutes).")
            return
        
        minutes = int(text)
        reminder_content = temp_data.get(user_id)
        
        # Обов'язково видаляємо стан ПЕРЕД запуском фонового завдання
        user_state.pop(user_id, None)
        temp_data.pop(user_id, None)

        # ВИПРАВЛЕНО: Додано дужки до get_main_keyboard()
        await update.message.reply_text(
            f"✅ Reminder set for {minutes} minute(s). I'm ready for new tasks!",
            reply_markup=get_main_keyboard()                          
        )
        
        # Фонова функція
        async def delayed_reminder(m_time, uid, msg):
            await asyncio.sleep(m_time * 60)
            try:
                await context.bot.send_message(chat_id=uid, text=f"⏰ REMINDER:\n{msg}")
            except Exception as e:
                print(f"Error sending reminder: {e}")

        # Запуск у фоні, щоб не блокувати text_handler
        asyncio.create_task(delayed_reminder(minutes, user_id, reminder_content))

# ---------- MAIN ----------
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    print("🤖 Bot is running...")
    app.run_polling()
