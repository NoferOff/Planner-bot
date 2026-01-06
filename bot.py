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
user_settings = {}
tasks = {}          # user_id -> list of tasks
user_state = {}     # user_id -> state
temp_data = {}      # user_id -> temp values (task index, reminder text)
MESSAGES = {
    "en": {
        "welcome": "👋 Welcome to the Planner bot!\n\nChoose an action:",
        "language_set": "✅ Language set to {lang}!",

        "new_plan": "🧹 New plan created. All tasks cleared.",
        "send_task": "✏️ Send the task text:",
        "no_tasks": "🗂 You have no tasks yet.",
        "your_tasks": "🗂 Your tasks:\n\n",

        "choose_task_priority": "⭐ Choose a task to set priority:",
        "choose_priority": "Choose priority level:",
        "priority_set": "✅ Priority set to {prio}!",

        "choose_task_deadline": "📅 Choose a task to set deadline:",
        "send_deadline": "📅 Type the deadline (e.g., '12:00' or 'Monday'):",
        "deadline_set": "✅ Deadline '{deadline}' saved!",

        "reminder_what": "⏰ What should I remind you about?",
        "reminder_minutes": "⏱ In how many minutes?",
        "reminder_set": "✅ Reminder set for {minutes} minute(s). I'm ready for new tasks!",
        "reminder_error": "❌ Please enter a number (minutes).",

        "progress": "📊 Progress:\nTotal tasks: {total}",

        "settings": "⚙️ Choose your settings:",
        "choose_language": "🌐 Choose language:",

        # Buttons
        "new_plan_btn": "➕ New Plan",
        "add_task_btn": "➕ Add Task",
        "my_tasks_btn": "🗂 My Tasks",
        "priorities_btn": "⭐ Priorities",
        "deadlines_btn": "📅 Deadlines",
        "reminders_btn": "⏰ Reminders",
        "progress_btn": "📊 Progress",
        "settings_btn": "⚙️ Settings",
        "language_btn": "Language",
        "reminders_enabled_btn": "Reminders Enabled",
        "default_priority_btn": "Default Priority",

        # Priority buttons
        "prio_low": "🟢 Low",
        "prio_medium": "🟡 Medium",
        "prio_high": "🔴 High",

        # Labels
        "priority": "Priority",
        "deadline": "Deadline",

        # Errors / info
        "no_tasks_priority": "⭐ No tasks to prioritize.",
        "no_tasks_deadline": "📅 No tasks to set deadlines."
    },

    "de": {
        "welcome": "👋 Willkommen beim Planer-Bot!\n\nWähle eine Aktion:",
        "language_set": "✅ Sprache auf {lang} gesetzt!",

        "new_plan": "🧹 Neuer Plan erstellt. Alle Aufgaben wurden gelöscht.",
        "send_task": "✏️ Sende den Aufgabentext:",
        "no_tasks": "🗂 Du hast noch keine Aufgaben.",
        "your_tasks": "🗂 Deine Aufgaben:\n\n",

        "choose_task_priority": "⭐ Wähle eine Aufgabe für die Priorität:",
        "choose_priority": "Wähle Prioritätsstufe:",
        "priority_set": "✅ Priorität auf {prio} gesetzt!",

        "choose_task_deadline": "📅 Wähle eine Aufgabe für die Deadline:",
        "send_deadline": "📅 Gib die Deadline ein (z. B. '12:00' oder 'Montag'):",
        "deadline_set": "✅ Deadline '{deadline}' gespeichert!",

        "reminder_what": "⏰ Woran soll ich dich erinnern?",
        "reminder_minutes": "⏱ In wie vielen Minuten?",
        "reminder_set": "✅ Erinnerung in {minutes} Minute(n) gesetzt! ",
        "reminder_error": "❌ Bitte gib eine Zahl (Minuten) ein.",

        "progress": "📊 Fortschritt:\nGesamtanzahl Aufgaben: {total}",

        "settings": "⚙️ Einstellungen auswählen:",
        "choose_language": "🌐 Sprache auswählen:",

        # Buttons
        "new_plan_btn": "➕ Neuer Plan",
        "add_task_btn": "➕ Aufgabe hinzufügen",
        "my_tasks_btn": "🗂 Meine Aufgaben",
        "priorities_btn": "⭐ Prioritäten",
        "deadlines_btn": "📅 Deadlines",
        "reminders_btn": "⏰ Erinnerungen",
        "progress_btn": "📊 Fortschritt",
        "settings_btn": "⚙️ Einstellungen",
        "language_btn": "Sprache",
        "reminders_enabled_btn": "Erinnerungen aktiv",
        "default_priority_btn": "Standardpriorität",

        # Priority buttons
        "prio_low": "🟢 Niedrig",
        "prio_medium": "🟡 Mittel",
        "prio_high": "🔴 Hoch",

        # Labels
        "priority": "Priorität",
        "deadline": "Deadline",

        # Errors / info
        "no_tasks_priority": "⭐ Keine Aufgaben zur Priorisierung.",
        "no_tasks_deadline": "📅 Keine Aufgaben für Deadlines."
    },

    "ua": {
        "welcome": "👋 Ласкаво просимо до Планер-бота!\n\nОберіть дію:",
        "language_set": "✅ Мову встановлено: {lang}!",

        "new_plan": "🧹 Новий план створено. Усі завдання видалено.",
        "send_task": "✏️ Надішліть текст завдання:",
        "no_tasks": "🗂 У вас поки немає завдань.",
        "your_tasks": "🗂 Ваші завдання:\n\n",

        "choose_task_priority": "⭐ Оберіть завдання для встановлення пріоритету:",
        "choose_priority": "Оберіть рівень пріоритету:",
        "priority_set": "✅ Пріоритет встановлено: {prio}!",

        "choose_task_deadline": "📅 Оберіть завдання для встановлення дедлайну:",
        "send_deadline": "📅 Введіть дедлайн (наприклад, '12:00' або 'Понеділок'):",
        "deadline_set": "✅ Дедлайн '{deadline}' збережено!",

        "reminder_what": "⏰ Про що нагадати?",
        "reminder_minutes": "⏱ Через скільки хвилин?",
        "reminder_set": "✅ Нагадування встановлено через {minutes} хв.",
        "reminder_error": "❌ Введіть число (хвилини).",

        "progress": "📊 Прогрес:\nЗагальна кількість завдань: {total}",

        "settings": "⚙️ Оберіть налаштування:",
        "choose_language": "🌐 Оберіть мову:",

        # Buttons
        "new_plan_btn": "➕ Новий план",
        "add_task_btn": "➕ Додати завдання",
        "my_tasks_btn": "🗂 Мої завдання",
        "priorities_btn": "⭐ Пріоритети",
        "deadlines_btn": "📅 Дедлайни",
        "reminders_btn": "⏰ Нагадування",
        "progress_btn": "📊 Прогрес",
        "settings_btn": "⚙️ Налаштування",
        "language_btn": "Мова",
        "reminders_enabled_btn": "Нагадування активні",
        "default_priority_btn": "Стандартний пріоритет",

        # Priority buttons
        "prio_low": "🟢 Низький",
        "prio_medium": "🟡 Середній",
        "prio_high": "🔴 Високий",

        # Labels
        "priority": "Пріоритет",
        "deadline": "Дедлайн",

        # Errors / info
        "no_tasks_priority": "⭐ Немає завдань для пріоритетів.",
        "no_tasks_deadline": "📅 Немає завдань для дедлайнів."
    }
}


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
   user_id = update.message.from_user.id
   lang = user_settings.get(user_id, {}).get("language","en")

   await update.message.reply_text(
       MESSAGES[lang]["welcome"],
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
        await query.message.edit_text(MESSAGES[lang]["new_plan"], reply_markup=get_main_keyboard())

    # 2. ADD TASK
    elif data == "add_task":
        user_state[user_id] = "WAIT_TASK"
        await query.message.edit_text(MESSAGES[lang]["add_task"], reply_markup=None)

    # 3. MY TASKS
    elif data == "my_tasks":
        if not tasks[user_id]:
            await query.message.edit_text(MESSAGES[lang]["my_task"], reply_markup=get_main_keyboard())
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
        await query.message.edit_text(f"📊 Progress:\nTotal tasks: {total}", reply_markup=get_main_keyboard())

    # 8. SETTINGS
    elif data == "settings":
        user_settings.setdefault(user_id, {
         "language": "en",        
         "reminders_enabled": True,
         "default_priority": "Medium"
        })
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("language", callback_data = "pick_settings_lang")],
            [InlineKeyboardButton("reminders_enabled", callback_data = "pick_settings_remin")],
            [InlineKeyboardButton("default_priority", callback_data = "pick_settings_prio")]
        ])
        
        await query.message.edit_text(
            "🌐 Choose your settings:",
              reply_markup=keyboard
        )
    
    # Priority Selection
    elif data.startswith("pick_pri_"):
        temp_data[user_id] = int(data.split("_")[-1])
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🟢 Low", callback_data="set_pri_Low")],
            [InlineKeyboardButton("🟡 Medium", callback_data="set_pri_Medium")],
            [InlineKeyboardButton("🔴 High", callback_data="set_pri_High")]
        ])
        await query.message.edit_text("Choose priority level:", reply_markup=keyboard)

    elif data.startswith("set_pri_"):
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





    elif data == "pick_settings_lang":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("English", callback_data="set_lang_en")],
            [InlineKeyboardButton("Deutsch", callback_data="set_lang_de")],
            [InlineKeyboardButton("Українська", callback_data="set_lang_ua")]
        ])
        await query.message.edit_text("Choose language:\n", reply_markup=keyboard)

    elif data.startswith("set_lang_"):
       lang = data.split("_")[-1]  # en / de / ua
       user_settings.setdefault(user_id, {})["language"] = lang
       await query.message.edit_text(
           MESSAGES[lang]["language_set"].format(lang=lang.upper()),
        reply_markup=get_main_keyboard()
       )

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
