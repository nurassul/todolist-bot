from aiogram.fsm.state import StatesGroup, State


# Для передачи состояния готовые поля
# Тут для создания таска
class TaskFSM(StatesGroup):
    waiting_title = State()
    waiting_description = State()
    waiting_priority = State()
    waiting_date = State()
    waiting_time = State()

# Тут про модификацию таска
class EditTaskFSM(StatesGroup):
    choosing_field = State()
    waiting_for_new_value = State()
    waiting_for_new_date = State()
    waiting_for_new_time = State()


