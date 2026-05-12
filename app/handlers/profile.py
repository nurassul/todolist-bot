from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart

from app.db import register_user, get_active_tasks, get_user_profile_stats
from app.keyboard.kb import main_menu

router = Router()

# Чисто для обработки про профиль юзера
# Выводим информацию про юзера и типо статистику задач.
@router.message(F.text == "👤 My Profile")
async def show_profile(message: Message):
    stats = await get_user_profile_stats(message.from_user.id)

    if not stats:
        await message.answer("User not found 😔. Enter /start to register")
        return

    username_text = f"@{stats['username']}" if stats['username'] else "Not found"
    reg_date = stats["created_at"].strftime("%d.%m.%Y")

    text = (
        f"👤 <b>Your profile</b>\n\n"
        f"<b>ID:</b> <code>{message.from_user.id}</code>\n"
        f"<b>Username:</b> {username_text}\n"
        f"<b>With us from:</b> {reg_date}\n\n"
        f"📊 <b>Task statistics:</b>\n"
        f"▫️ Total created: <b>{stats['total']}</b>\n"
        f"▫️ In progress: <b>{stats['active']}</b> ⏳\n"
        f"▫️ Completed: <b>{stats['completed']}</b> ✅\n"
    )

    if stats['total'] > 0 and stats['active'] == 0:
        text += "\n🎉 <i>Great job! All tasks are closed.</i>"

    await message.answer(text, reply_markup=main_menu())
