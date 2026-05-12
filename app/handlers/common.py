from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart

from app.db import register_user, get_active_tasks
from app.keyboard.kb import main_menu

router = Router()


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