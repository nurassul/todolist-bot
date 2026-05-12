from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def main_menu() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="📋 My Tasks"),
        KeyboardButton(text="📝 Add task")
    )
    builder.row(
        KeyboardButton(text="👤 My Profile"),
        KeyboardButton(text="🔍 Help")
    )
    return builder.as_markup(resize_keyboard=True)


def deadline_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Today", callback_data="deadline_today"),
        InlineKeyboardButton(text="Tomorrow", callback_data="deadline_tomorrow")
    )
    builder.row(
        InlineKeyboardButton(text="📅 Select date", callback_data="deadline_custom")
    )
    return builder.as_markup()


def task_priority_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🟢 Low", callback_data="priority_1"),
        InlineKeyboardButton(text="🟡 Medium", callback_data="priority_2"),
        InlineKeyboardButton(text="🔴 High", callback_data="priority_3")
    )
    return builder.as_markup()

def task_kb(task_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Done", callback_data=f"done_{task_id}"),
        InlineKeyboardButton(text="🗑 Delete", callback_data=f"delete_{task_id}")
    )
    builder.row(
        InlineKeyboardButton(text="✏️ Edit", callback_data=f"edit_start_{task_id}")
    )
    return builder.as_markup()

def edit_field_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📝 Title", callback_data="field_title"),
        InlineKeyboardButton(text="📄 Description", callback_data="field_description"),
    )
    builder.row(
        InlineKeyboardButton(text="⏳ Deadline", callback_data="field_deadline"),
        InlineKeyboardButton(text="🔥 Priority", callback_data="field_priority")
    )
    builder.row(
        InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_edit")
    )
    return builder.as_markup()