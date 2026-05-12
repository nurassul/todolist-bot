import logging
from datetime import timedelta
from aiogram import Bot

from app.db import get_upcoming_deadlines


async def check_and_send_deadlines(bot: Bot):
    try:
        reminders = [
            (28, 30, "⏰ <b>30 minutes</b> left! Time to wrap things up."),
            (13, 15, "⏳ Only <b>15 minutes</b> left. Get going!"),
            (3, 5, "📢 Attention! <b>5 minutes</b> left."),
            (0, 2, "🔥 <b>DEADLINE!</b> Time is up or about to run out!")]
        for min_m, max_m, deadline_text in reminders:
            tasks = await get_upcoming_deadlines(min_m, max_m)
            if not tasks:
                continue
            for task in tasks:
                text = (
                    f"⚠️ <b>Deadline Reminder!</b>\n\n"
                    f"📌 <b>{task.title}</b>\n"
                    f"{deadline_text}"
                )
                try:
                    await bot.send_message(chat_id=task.user_id, text=text)
                except Exception as e:
                    logging.error(f"Error sending message to user: {task.user_id}: {e}")

    except Exception as e:
        logging.error(f"Error in checking deadlines: {e}")
