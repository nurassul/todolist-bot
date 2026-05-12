# To-Do List Telegram Bot

A Telegram bot for personal task management with deadlines, priorities, editing, and automatic reminder notifications.

## What This Bot Does

The bot helps users manage their day-to-day tasks directly in Telegram:
- Registers a user on first `/start`
- Creates tasks with title, optional description, priority, and strict deadline
- Shows active tasks sorted by priority and deadline
- Lets users mark tasks as done, edit fields, or delete tasks
- Sends automatic deadline reminders before tasks expire
- Shows a personal profile with task statistics

## Features

- Task creation flow with FSM (step-by-step):
  - Title
  - Description (or `/skip`)
  - Priority (`Low`, `Medium`, `High`)
  - Deadline date (calendar picker)
  - Deadline time (`HH:MM`)
- Task management:
  - `My Tasks` / `/tasks`
  - Inline actions: `Done`, `Edit`, `Delete`
- Task editing:
  - Edit `title`, `description`, `priority`, `deadline`
- Validation:
  - Prevents selecting past dates
  - Prevents saving past time for current date
  - Validates time format
- Smart reminders (scheduler job every minute):
  - ~30 minutes before deadline
  - ~15 minutes before deadline
  - ~5 minutes before deadline
  - Final alert at deadline window
- User profile:
  - Telegram ID
  - Username
  - Registration date
  - Total / active / completed tasks
- Help command with built-in usage guide

## Tech Stack

- Python 3.11
- [aiogram 3](https://github.com/aiogram/aiogram) - Telegram Bot framework (async)
- [SQLAlchemy 2 (async)](https://docs.sqlalchemy.org/) - ORM and async DB layer
- [asyncpg](https://github.com/MagicStack/asyncpg) - PostgreSQL async driver
- [APScheduler](https://apscheduler.readthedocs.io/) - background reminder scheduler
- [aiogram-calendar](https://pypi.org/project/aiogram-calendar/) - inline date picker
- PostgreSQL 16
- Docker + Docker Compose

## Project Structure

```text
app/
  main.py                 # bot entrypoint, routers, scheduler startup
  db.py                   # DB models + queries (users/tasks)
  scheduler.py            # deadline reminder logic
  handlers/
    common.py             # /start, /help
    taskboarding.py       # create/view/edit/delete/complete task flows
    profile.py            # user profile and stats
    states.py             # FSM states
  keyboard/
    kb.py                 # reply + inline keyboards
Dockerfile
Docker-compose.yaml
init.sql
requirements.txt
```

## Commands and UI Actions

### Bot commands
- `/start` - register user and open main menu
- `/add` - create new task
- `/tasks` - show active tasks
- `/help` - show help
- `/cancel` - cancel current FSM action

### Main menu buttons
- `My Tasks`
- `Add task`
- `My Profile`
- `Help`

## Data Model

### `users`
- `user_tg_id` (PK)
- `username`
- `created_at`

### `tasks`
- `id` (PK)
- `user_id` (FK -> users.user_tg_id)
- `title`
- `description`
- `priority` (`1..3`)
- `deadline`
- `is_completed`
- `created_at`

## Environment Variables

Required:
- `BOT_TOKEN` - Telegram bot token from BotFather

For local DB / compose:
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_DB`

Used by app:
- `DATABASE_URL`
  - Default in code: `postgresql+asyncpg://postgres:postgres@postgres:5432/todolist`

Example `.env`:

```env
BOT_TOKEN=your_telegram_bot_token
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=todolist
```

## Run with Docker Compose (recommended)

1. Create `.env` file in project root.
2. Build and run services:

```bash
docker compose up --build
```

3. The stack starts:
- `postgres` (with `init.sql` initialization)
- `bot` (polling Telegram updates)

To stop:

```bash
docker compose down
```

## Run Locally (without Docker)

1. Create and activate virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start PostgreSQL and create DB/tables (run `init.sql`).
4. Export environment variables (`BOT_TOKEN`, `DATABASE_URL`).
5. Run bot:

```bash
python -m app.main
```

## Notes

- Timezone in scheduler and DB deadline checks is configured for `Asia/Almaty`.
- Scheduler checks deadlines every minute.
- FSM storage is in-memory (`MemoryStorage`), so temporary dialog states are not persisted across bot restarts.

## Future Improvements (optional)

- Add recurring tasks
- Add pagination for long task lists
- Add task search/filter by priority/date
- Add Redis FSM storage for production resiliency
- Add unit/integration tests


