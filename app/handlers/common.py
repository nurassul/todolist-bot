from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart

from app.db import register_user, get_active_tasks
from app.keyboard.kb import main_menu

router = Router()


# Чисто для обработки базовых команд.
# /start /help

# ───────────────────────── /start ─────────────────────────

# Для обработки команды /start
# Просто саламкаемся и проверяем зареган ли юзер
# Если зареган просто в меню отправляем
@router.message(CommandStart())
async def cmd_start(msg: Message):
    await register_user(msg.from_user.id, msg.from_user.username)

    tasks = await get_active_tasks(msg.from_user.id)
    if tasks:
        await msg.answer(
            f"Welcome back!\n"
            f"Use the menu below to get started.",
            reply_markup=main_menu()
        )
        return
    await msg.answer(
        f"😊 Hello, dear user!\n\n"
        f"I'm your To-Do bot 📝. I'll help you manage your tasks and send you notifications, "
        f"so you don't miss a thing.\n\n"
        f"Use the menu below to get started.",
        reply_markup=main_menu()
    )


# Тут показываем всю инфу про наш бот и какие команды есть
@router.message(F.text == "🔍 Help")
@router.message(F.text == "/help")
async def show_help(msg: Message):
    text =(
        "🛠 <b>How to use this bot</b>\n\n"
        "I am your personal task manager. I will help you track your deadlines and send you reminders so you never miss anything!\n\n"
        "📌 <b>Main Commands:</b>\n"
        "<b>/start</b> — Open the main menu.\n"
        "<b>/add</b> — Create a new task.\n"
        "<b>/cancel</b> — Stop any current action.\n"
        "<b>/tasks</b> — Show all tasks.\n\n"
        "🎯 <b>Features:</b>\n"
        "📝 <b>Add task:</b> Create a task with a title, description, priority (🔴 High, 🟡 Medium, 🟢 Low), and a strict deadline.\n"
        "📋 <b>My Tasks:</b> View all your active tasks. Under each task, you can use buttons to:\n"
        "  ✅ <b>Done</b> — Mark the task as completed.\n"
        "  ✏️ <b>Edit</b> — Change the title, description, priority, or deadline.\n"
        "  🗑 <b>Delete</b> — Remove the task permanently.\n\n"
        "⏰ <b>Smart Reminders:</b>\n"
        "I will automatically notify you <b>30, 15, and 5 minutes</b> before your deadline, and send a final alert when the time is up!\n\n"
    )
    await msg.answer(text, reply_markup=main_menu())