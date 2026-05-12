from datetime import datetime

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback
from zoneinfo import ZoneInfo

from app import db
from app.db import register_user, get_active_tasks, mark_task_completed, update_task_field, save_user_tasks
from app.handlers.states import EditTaskFSM, TaskFSM
from app.keyboard.kb import main_menu, task_kb, edit_field_kb, task_priority_kb

router = Router()


# ───────────────────────── Main menu ─────────────────────────

# ──────────────── Working with tasks ────────────────────
# Показать все задачи юзера
# И вешаем над каждым заданием кб
@router.message(F.text == "📋 My Tasks")
@router.message(F.text == "/tasks")
async def show_all_tasks(msg: Message):
    tasks = await get_active_tasks(msg.from_user.id)
    if not tasks:
        await msg.answer(
            f"🎉 You don't have active tasks!"
        )

    for task in tasks:
        prio = {3: "🔴", 2: "🟡", 1: "🟢"}.get(task.priority, "🟢")
        local_deadline = task.deadline.astimezone(ZoneInfo("Asia/Almaty"))

        text = (
            f"📌 Title: <b>{task.title}</b>\n"
            f"🔥 Priority: {prio}\n"
            f"📝 Description:\n{task.description if task.deadline else 'No description.'}\n"
            f"⏳ Deadline: {local_deadline.strftime('%d.%m.%Y %H:%M')}"
        )
        await msg.answer(text, reply_markup=task_kb(task.id))


# Просто поменять статус как done
@router.callback_query(F.data.startswith("done_"))
async def complete_task(callback: CallbackQuery):
    task_id = int(callback.data.split("_")[1])

    await mark_task_completed(task_id)

    old_text = callback.message.html_text
    await callback.message.edit_text(
        text=f"<s>{old_text}</s>\n\n<i>✨ Done!</i>",
        parse_mode="HTML",
        reply_markup=None
    )
    await callback.answer("Task closed!")


# Удалить задачу полностью
@router.callback_query(F.data.startswith("delete_"))
async def delete_task(callback: CallbackQuery):
    task_id = int(callback.data.split("_")[1])

    await db.delete_task(task_id)

    old_text = callback.message.html_text
    await callback.message.edit_text(
        text=f"<s>{old_text}</s>\n\n<i>❌ Deleted!</i>",
        parse_mode="HTML",
        reply_markup=None
    )
    await callback.answer("Task closed!")


# Начало редактирование
@router.callback_query(F.data.startswith("edit_start_"))
async def edit_task(callback: CallbackQuery, state: FSMContext):
    task_id = int(callback.data.split("_")[2])
    await state.update_data(edit_task_id=task_id)
    await callback.message.edit_text(
        f"What you want to edit?",
        reply_markup=edit_field_kb()
    )

    await state.set_state(EditTaskFSM.choosing_field)


# Отменить редактирование
@router.callback_query(F.data == "cancel_edit")
async def cancel_edit(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "❌ Editing was cancelled!"
    )
    await state.clear()


#  Выбрать поле которую меняем
@router.callback_query(F.data.startswith("field_"))
async def choose_edit_field(callback: CallbackQuery, state: FSMContext):
    field = callback.data.split("_")[1]
    await state.update_data(edit_field=field)

    if field in ("title", "description"):
        await callback.message.edit_text(f"✍️ Write a new {field} for task:")
        await state.set_state(EditTaskFSM.waiting_for_new_value)

    if field == "priority":
        await callback.message.edit_text(
            f"Choose a new priority:",
            reply_markup=task_priority_kb()
        )

    if field == "deadline":
        calendar = SimpleCalendar(show_alerts=True)
        await callback.message.edit_text(
            "📅 Выбери новую дату дедлайна:",
            reply_markup=await calendar.start_calendar()
        )
        await state.set_state(EditTaskFSM.waiting_for_new_date)


# Меняем тайтл или дескрипшион таска
@router.message(EditTaskFSM.waiting_for_new_value, F.text)
async def process_new_text(message: Message, state: FSMContext):
    data = await state.get_data()

    await update_task_field(data["edit_task_id"], data["edit_field"], message.text)
    await message.answer("✅ Successfully updated!")
    await state.clear()


# Меняем приоритет задачи
@router.callback_query(EditTaskFSM.choosing_field, F.data.startswith("priority_"))
async def process_new_priority(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    new_priority = int(callback.data.split("_")[1])

    await update_task_field(data["edit_task_id"], "priority", new_priority)

    await callback.message.edit_text("✅ Priority successfully updated!")
    await state.clear()


# Выбираем дату
@router.callback_query(EditTaskFSM.waiting_for_new_date, SimpleCalendarCallback.filter())
async def process_new_date(callback: CallbackQuery, callback_data: SimpleCalendarCallback, state: FSMContext):
    calendar = SimpleCalendar(show_alerts=True)
    selected, date = await calendar.process_selection(callback, callback_data)

    if selected:
        now = datetime.now()
        if date.date() < now.date():
            await callback.answer("⚠️ You can't select past date", show_alert=True)
            await callback.message.edit_text(
                "📅 Please select a valid date (today or in the future):",
                reply_markup=await SimpleCalendar().start_calendar()
            )
            return
        await state.update_data(new_date=date)
        await callback.message.edit_text(
            f"📅 New date: {date.strftime('%d.%m.%Y')}\n\n"
            f"⏰ Now write time (HH:MM):"
        )
        await state.set_state(EditTaskFSM.waiting_for_new_time)


# Выбираем время и сохраняем
@router.message(EditTaskFSM.waiting_for_new_time, F.text)
async def process_new_time(message: Message, state: FSMContext):
    data = await state.get_data()
    new_date = data["new_date"]

    try:
        parsed_time = datetime.strptime(message.text, "%H:%M").time()
        final_deadline = datetime.combine(new_date.date(), parsed_time)
    except ValueError:
        await message.answer("⚠️ Incorrect format. Write HH:MM (Like 14:30)")
        return

    await update_task_field(data["edit_task_id"], "deadline", final_deadline)

    await message.answer(f"✅ Deadline successfully changed to {final_deadline.strftime('%d.%m.%Y %H:%M')}")
    await state.clear()


# ───────────────────────── Adding tasks ─────────────────────────────
# Просто для отмены текущий действий.
@router.message(F.text.lower().in_(["отмена", "/cancel", "cancel"]))
async def cancel_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()
    await message.answer("❌ Cancelled adding task")


# Тут обрабатываем добавление задачи
# Стартовая точка здесь и начинаем с тайтла
@router.message(F.text == "📝 Add task")
@router.message(F.text == "/add")
async def add_task(msg: Message, state: FSMContext):
    await msg.answer(
        "📝 Let's create a new task!\n\n"
        "First, write the <b>Task title</b> (short):",
    )
    await state.set_state(TaskFSM.waiting_title)


# Получаем тайтл и дальше идем спрашиваем дескрипшн
# Состояние меняем на ждем дескрипшн
@router.message(TaskFSM.waiting_title, F.text)
async def process_title(msg: Message, state: FSMContext):
    await state.update_data(title=msg.text)
    await msg.answer(
        f"Great. Now add a <b>description</b> or details.\n"
        f"If you don't want to write description write /skip"
    )
    await state.set_state(TaskFSM.waiting_description)

# Получаем дескрипшн если /skip тогда без дескришн
# Теперь ждем приоритет
@router.message(TaskFSM.waiting_description, F.text)
async def process_description(msg: Message, state: FSMContext):
    desc = "" if msg.text == "/skip" else msg.text
    await state.update_data(description=desc)
    await msg.answer(
        f"Cool! Now choose priority of task",
        reply_markup=task_priority_kb()
    )
    await state.set_state(TaskFSM.waiting_priority)

# Inline кнопкой получаем приоритет
# Дальше ждем дату
@router.callback_query(TaskFSM.waiting_priority, F.data.startswith("priority_"))
async def process_priority(callback: CallbackQuery, state: FSMContext):
    priority_level = int(callback.data.split("_")[1])
    await state.update_data(priority=priority_level)

    calendar = SimpleCalendar(show_alerts=True)
    await callback.message.edit_text(
        "📅 Choose <b>deadline date</b>:",
        reply_markup=await calendar.start_calendar(),
    )
    await state.set_state(TaskFSM.waiting_date)


# Выводим календарь и юзер выбирает дату
# Ждем ввода времени
@router.callback_query(TaskFSM.waiting_date, SimpleCalendarCallback.filter())
async def process_date(callback: CallbackQuery, callback_data: SimpleCalendarCallback, state: FSMContext):
    calendar = SimpleCalendar(show_alerts=True)
    selected, date = await calendar.process_selection(callback, callback_data)

    if selected:
        now = datetime.now()
        if date.date() < now.date():
            await callback.answer("⚠️ You can't select past date", show_alert=True)
            await callback.message.edit_text(
                "📅 Please select a valid date (today or in the future):",
                reply_markup=await SimpleCalendar().start_calendar()
            )
            return
        await state.update_data(deadline_date=date)
        await callback.message.edit_text(
            f"📅 Date: <b>{date.strftime('%d.%m.%Y')}</b>\n\n"
            f"⏰ Now enter <b>the exact time</b> (for example, 2:30 PM).\n"
        )
        await state.set_state(TaskFSM.waiting_time)


# Юзер написал время и сохраняем все
@router.message(TaskFSM.waiting_time, F.text)
async def process_time_and_save(message: Message, state: FSMContext):
    data = await state.get_data()
    selected_date = data["deadline_date"]
    now = datetime.now()
    try:
        parsed_time = datetime.strptime(message.text, "%H:%M").time()
        final_deadline = datetime.combine(selected_date.date(), parsed_time)
    except ValueError:
        await message.answer("⚠️ Invalid time format. Please enter HH:MM (like 09:15)")
        return

    if final_deadline < now:
        await message.answer(
            "⚠️ This time has already passed!\n"
            "Enter a time in the future or press /cancel to cancel."
        )
        return

    await save_user_tasks(
        message.from_user.id,
        data["title"],
        data["description"],
        data["priority"],
        final_deadline
    )

    prio_emoji = {3: "🔴", 2: "🟡", 1: "🟢"}.get(data["priority"])

    success_text = (
        f"✅ <b>Task successfully created!</b>\n\n"
        f"📌 Title: <b>{data['title']}</b>\n"
        f"📝 Description:\n<i>{data['description'] if data['description'] else 'No description'}</i>\n"
        f"🔥 Priority: {prio_emoji}\n"
        f"⏳ Deadline: {final_deadline.strftime('%d.%m.%Y %H:%M')}"
    )

    await message.answer(success_text, reply_markup=main_menu())
    await state.clear()

