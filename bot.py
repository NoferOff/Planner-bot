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
reminder_tasks = {} # user_id -> list of reminder tasks
user_state = {}     # user_id -> state
temp_data = {}      # user_id -> temp values (task index, reminder text)

# ---------- MESSAGES ----------
MESSAGES = {
    "en": {
        "welcome": "👋 Welcome to the Planner bot!\n\nChoose an action:",
        "language_set": "✅ Language set to {lang}!",
        "new_plan": "🧹 New plan created. All tasks cleared.",
        "send_task": "✏️ Send the task text:",
        "task_added": "✅ Task '{task}' added!",
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
        "choose_reminder_type": "⏰ Choose reminder settings:",
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
        "prio_low": "🟢 Low",
        "prio_medium": "🟡 Medium",
        "prio_high": "🔴 High",
        "priority": "Priority",
        "deadline": "Deadline",
        "no_tasks_priority": "⭐ No tasks to prioritize.",
        "no_tasks_deadline": "📅 No tasks to set deadlines."
    },
    "de": {
        "welcome": "👋 Willkommen beim Planer-Bot!\n\nWähle eine Aktion:",
        "language_set": "✅ Sprache auf {lang} gesetzt!",
        "new_plan": "🧹 Neuer Plan erstellt. Alle Aufgaben wurden gelöscht.",
        "send_task": "✏️ Sende den Aufgabentext:",
        "task_added": "✅ Aufgabe '{task}' hinzugefügt!",
        "no_tasks": "🗂 Du hast noch keine Aufgaben.",
        "your_tasks": "🗂 Deine Aufgaben:\n\n",
        "choose_task_priority": "⭐ Wähle eine Aufgabe für die Priorität:",
        "choose_priority": "Prioritätsstufe wählen:",
        "priority_set": "✅ Priorität auf {prio} gesetzt!",
        "choose_task_deadline": "📅 Wähle eine Aufgabe für die Deadline:",
        "send_deadline": "📅 Gib die Deadline ein (z. B. '12:00' oder 'Montag'):",
        "deadline_set": "✅ Deadline '{deadline}' gespeichert!",
        "reminder_what": "⏰ Woran soll ich dich erinnern?",
        "reminder_minutes": "⏱ In wie vielen Minuten?",
        "reminder_set": "✅ Erinnerung in {minutes} Minute(n) gesetzt!",
        "reminder_error": "❌ Bitte gib eine Zahl (Minuten) ein.",
        "progress": "📊 Fortschritt:\nGesamtanzahl Aufgaben: {total}",
        "settings": "⚙️ Einstellungen auswählen:",
        "choose_language": "🌐 Sprache auswählen:",
        "choose_reminder_type": "⏰ Erinnerungseinstellungen wählen:",
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
        "prio_low": "🟢 Niedrig",
        "prio_medium": "🟡 Mittel",
        "prio_high": "🔴 Hoch",
        "priority": "Priorität",
        "deadline": "Deadline",
        "no_tasks_priority": "⭐ Keine Aufgaben zur Priorisierung.",
        "no_tasks_deadline": "📅 Keine Aufgaben für Deadlines."
    },
    "ua": {
        "welcome": "👋 Ласкаво просимо до Планер-бота!\n\nОберіть дію:",
        "language_set": "✅ Мову встановлено: {lang}!",
        "new_plan": "🧹 Новий план створено. Усі завдання видалено.",
        "send_task": "✏️ Надішліть текст завдання:",
        "task_added": "✅ Завдання '{task}' додано!",
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
        "choose_reminder_type": "⏰ Оберіть налаштування нагадувань:",
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
        "prio_low": "🟢 Низький",
        "prio_medium": "🟡 Середній",
        "prio_high": "🔴 Високий",
        "priority": "Пріоритет",
        "deadline": "Дедлайн",
        "no_tasks_priority": "⭐ Немає завдань для пріоритетів.",
        "no_tasks_deadline": "📅 Немає завдань для дедлайнів."
    }
}

# ---------- HELPERS ----------
def t(user_id, key):
    """Повертає повідомлення або кнопку на мові користувача"""
    lang = user_settings.get(user_id, {}).get("language", "en")
    return MESSAGES[lang].get(key, key)

async def maybe_sleep(user_id, seconds):
    """
    Sleep only if reminders are enabled for this user
    """
    if user_settings.get(user_id, {}).get("reminders_enabled", True):
        await asyncio.sleep(seconds)

def cancel_user_reminders(user_id):
     tasks_to_cancel = reminder_tasks.get(user_id, [])
     for t in tasks_to_cancel:
        t.cancel()
     reminder_tasks[user_id] = []

def get_main_keyboard(user_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t(user_id, "new_plan_btn"), callback_data="new_plan")],
        [InlineKeyboardButton(t(user_id, "add_task_btn"), callback_data="add_task")],
        [InlineKeyboardButton(t(user_id, "my_tasks_btn"), callback_data="my_tasks")],
        [InlineKeyboardButton(t(user_id, "priorities_btn"), callback_data="priorities")],
        [InlineKeyboardButton(t(user_id, "deadlines_btn"), callback_data="deadlines")],
        [InlineKeyboardButton(t(user_id, "reminders_btn"), callback_data="reminders")],
        [InlineKeyboardButton(t(user_id, "progress_btn"), callback_data="progress")],
        [InlineKeyboardButton(t(user_id, "settings_btn"), callback_data="settings")]
    ])

# ---------- /START ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    await update.message.reply_text(
        t(user_id, "welcome"),
        reply_markup=get_main_keyboard(user_id)
    )

# ---------- BUTTON HANDLER ----------
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data
    tasks.setdefault(user_id, [])
    await query.answer()

    # NEW PLAN
    if data == "new_plan":
        tasks[user_id] = []
        await query.message.edit_text(t(user_id, "new_plan"), reply_markup=get_main_keyboard(user_id))

    # ADD TASK
    elif data == "add_task":
        user_state[user_id] = "WAIT_TASK"
        await query.message.edit_text(t(user_id, "send_task"), reply_markup=None)

    # MY TASKS
    elif data == "my_tasks":
        if not tasks[user_id]:
            await query.message.edit_text(t(user_id, "no_tasks"), reply_markup=get_main_keyboard(user_id))
        else:
            if setdefaults := user_settings.get(user_id, {}).get("default_priority"):
                for tsk in tasks[user_id]:
                    if tsk["priority"] == "Medium":
                        tsk["priority"] = setdefaults
            text = t(user_id, "your_tasks")
            for i, tsk in enumerate(tasks[user_id], 1):
                text += f"{i}. {tsk['text']} | {t(user_id, 'priority')}: {tsk['priority']} | {t(user_id, 'deadline')}: {tsk['deadline']}\n"
            await query.message.edit_text(text, reply_markup=get_main_keyboard(user_id))

    # PRIORITIES
    elif data == "priorities":
        if not tasks[user_id]:
            await query.message.edit_text(t(user_id, "no_tasks_priority"), reply_markup=get_main_keyboard(user_id))
        else:
            buttons = [[InlineKeyboardButton(f"{i+1}. {tsk['text']}", callback_data=f"pick_pri_{i}")] for i, tsk in enumerate(tasks[user_id])]
            await query.message.edit_text(t(user_id, "choose_task_priority"), reply_markup=InlineKeyboardMarkup(buttons))

    # DEADLINES
    elif data == "deadlines":
        if not tasks[user_id]:
            await query.message.edit_text(t(user_id, "no_tasks_deadline"), reply_markup=get_main_keyboard(user_id))
        else:
            buttons = [[InlineKeyboardButton(f"{i+1}. {tsk['text']}", callback_data=f"pick_dead_{i}")] for i, tsk in enumerate(tasks[user_id])]
            await query.message.edit_text(t(user_id, "choose_task_deadline"), reply_markup=InlineKeyboardMarkup(buttons))

    # REMINDERS
    elif data == "reminders":
        user_state[user_id] = "WAIT_REMINDER_TEXT"
        if not user_settings.get(user_id, {}).get("reminders_enabled", True):
            await query.message.edit_text("⏰ Reminders are currently disabled. You can enable them in Settings.", reply_markup=get_main_keyboard(user_id))
            return
        
        try:
          await query.message.edit_text(t(user_id, "reminder_what"), reply_markup=None)
        except asyncio.CancelledError:
            print(f"Reminder for user {user_id} cancelled")

    # PROGRESS
    elif data == "progress":
        total = len(tasks[user_id])
        await query.message.edit_text(t(user_id, "progress").format(total=total), reply_markup=get_main_keyboard(user_id))

    # SETTINGS
    elif data == "settings":
        user_settings.setdefault(user_id, {"language": "en","reminders_enabled": True,"default_priority": "Medium"})
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(t(user_id, "language_btn"), callback_data="pick_settings_lang")],
            [InlineKeyboardButton(t(user_id, "reminders_enabled_btn"), callback_data="pick_settings_remin")],
            [InlineKeyboardButton(t(user_id, "default_priority_btn"), callback_data="pick_settings_prio")]
        ])
        await query.message.edit_text(t(user_id, "settings"), reply_markup=keyboard)

    # Priority selection
    elif data.startswith("pick_pri_"):
        temp_data[user_id] = int(data.split("_")[-1])
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(t(user_id, "prio_low"), callback_data="set_pri_Low")],
            [InlineKeyboardButton(t(user_id, "prio_medium"), callback_data="set_pri_Medium")],
            [InlineKeyboardButton(t(user_id, "prio_high"), callback_data="set_pri_High")]
        ])
        await query.message.edit_text(t(user_id, "choose_priority"), reply_markup=keyboard)

    elif data.startswith("set_pri_"):
        prio = data.split("_")[-1]
        idx = temp_data.get(user_id)
        if idx is not None:
            tasks[user_id][idx]["priority"] = prio
        user_state.pop(user_id, None)
        temp_data.pop(user_id, None)
        await query.message.edit_text(t(user_id, "priority_set").format(prio=prio), reply_markup=get_main_keyboard(user_id))

    # Deadline input
    elif data.startswith("pick_dead_"):
        temp_data[user_id] = int(data.split("_")[-1])
        user_state[user_id] = "WAIT_DEADLINE_INPUT"
        await query.message.edit_text(t(user_id, "send_deadline"), reply_markup=None)

    # Language selection
    elif data == "pick_settings_lang":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("English", callback_data="set_lang_en")],
            [InlineKeyboardButton("Deutsch", callback_data="set_lang_de")],
            [InlineKeyboardButton("Українська", callback_data="set_lang_ua")]
        ])
        await query.message.edit_text(t(user_id, "choose_language"), reply_markup=keyboard)

    elif data.startswith("set_lang_"):
        lang = data.split("_")[-1]
        user_settings.setdefault(user_id, {})["language"] = lang
        await query.message.edit_text(t(user_id, "language_set").format(lang=lang.upper()), reply_markup=get_main_keyboard(user_id))

    elif data =="pick_settings_remin":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("ON", callback_data = "set_remin_on")],
            [InlineKeyboardButton("OFF", callback_data = "set_remin_off")]
        ])
        await query.message.edit_text(t(user_id,"choose the type of reminders"), reply_markup=keyboard)

    elif data == "set_remin_on":
        user_settings.setdefault(user_id, {})["reminders_enabled"] = True
        await query.message.edit_text("⏰ Reminders are enabled", reply_markup=get_main_keyboard(user_id))

    elif data == "set_remin_off":
        user_settings.setdefault(user_id, {})["reminders_enabled"] = False
        cancel_user_reminders(user_id)  
        await query.message.edit_text("⏰ Reminders are disabled", reply_markup=get_main_keyboard(user_id))

    elif data == "pick_settings_prio":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Low", callback_data="settings_prio_Low")],
            [InlineKeyboardButton("Medium", callback_data="settings_prio_Medium")],
            [InlineKeyboardButton("High", callback_data="settings_prio_High")]
        ])
        await query.message.edit_text(t(user_id, "choose_priority"), reply_markup=keyboard)

    elif data.startswith("settings_prio_"):
        prio = data.split("_")[-1]
        user_settings.setdefault(user_id, {})["priority"] = prio
        await query.message.edit_text(t(user_id, "priority_set").format(prio=prio), reply_markup=get_main_keyboard(user_id))

    elif data == "settings_prio_Low":
        user_settings.setdefault(user_id, {})["default_priority"] = "prio_low"
        await query.message.edit_text(t(user_id, "priority_set").format(prio="Low"), reply_markup=get_main_keyboard(user_id))

    elif data == "settings_prio_Medium":
        user_settings.setdefault(user_id, {})["default_priority"] = "prio_medium"
        
        await query.message.edit_text(t(user_id, "priority_set").format(prio="Medium"), reply_markup=get_main_keyboard(user_id))

    elif data == "settings_prio_High":
        user_settings.setdefault(user_id, {})["default_priority"] = "prio_high"
        await query.message.edit_text(t(user_id, "priority_set").format(prio="High"), reply_markup=get_main_keyboard(user_id))

# ---------- TEXT HANDLER ----------
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text
    state = user_state.get(user_id)

    # ADD TASK
    if state == "WAIT_TASK":
        default_prio = user_settings.get(user_id, {}).get("default_priority", "Medium")
        tasks.setdefault(user_id, []).append({
             "text": text,
             "priority": default_prio,
             "deadline": "None"
            })
        user_state.pop(user_id, None)
        await update.message.reply_text(t(user_id, "task_added").format(task=text), reply_markup=get_main_keyboard(user_id))

    # DEADLINE INPUT
    elif state == "WAIT_DEADLINE_INPUT":
        idx = temp_data.get(user_id)
        if idx is not None:
            tasks[user_id][idx]["deadline"] = text
            user_state.pop(user_id, None)
            temp_data.pop(user_id, None)
            await update.message.reply_text(t(user_id, "deadline_set").format(deadline=text), reply_markup=get_main_keyboard(user_id))

    # REMINDER TEXT
    elif state == "WAIT_REMINDER_TEXT":
        temp_data[user_id] = text
        user_state[user_id] = "WAIT_REMINDER_TIME"
        if not user_settings.get(user_id, {}).get("reminders_enabled", True):
            await update.message.reply_text(
            "⏰ Reminders are OFF. Enable them in Settings.", 
            reply_markup=get_main_keyboard(user_id)
            )
            user_state.pop(user_id, None)
            temp_data.pop(user_id, None)
            return
       
        await update.message.reply_text(t(user_id, "reminder_minutes"), reply_markup=None)
        

    # REMINDER TIME
    elif state == "WAIT_REMINDER_TIME":
        if not text.isdigit():
            await update.message.reply_text(t(user_id, "reminder_error"))
            return
        minutes = int(text)
        reminder_content = temp_data.get(user_id)
        user_state.pop(user_id, None)
        temp_data.pop(user_id, None)
        await update.message.reply_text(t(user_id, "reminder_set").format(minutes=minutes), reply_markup=get_main_keyboard(user_id))

        async def delayed_reminder(m_time, uid, msg):
            try:
                await maybe_sleep(uid, m_time * 60)
                if not user_settings.get(uid, {}).get("reminders_enabled", True):
                 return
                await context.bot.send_message(chat_id=uid, text=f"⏰ REMINDER:\n{msg}")
            except asyncio.CancelledError:
                print(f"Reminder for user {uid} cancelled")

        task = asyncio.create_task(delayed_reminder(minutes, user_id, reminder_content))
        reminder_tasks.setdefault(user_id, []).append(task)
# ---------- MAIN ----------
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    print("🤖 Bot is running...")
    app.run_polling()
