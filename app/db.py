import os
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from sqlalchemy import BigInteger, String, DateTime, func, Integer, Text, SmallInteger, Boolean, text, ForeignKey, \
     select, delete, update
from sqlalchemy.orm import mapped_column
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped
from sqlalchemy.dialects.postgresql import insert


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@postgres:5432/todolist"
)

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    user_tg_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.user_tg_id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    priority: Mapped[int] = mapped_column(SmallInteger, server_default="1")
    deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    is_completed: Mapped[bool] = mapped_column(Boolean, server_default=text("FALSE"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


async def register_user(user_id: int, username: str):
    async with AsyncSessionLocal() as session:
        stmt = insert(User).values(
            user_tg_id=user_id,
            username=username
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=["user_tg_id"],
            set_=dict(username=stmt.excluded.username)
        )
        await session.execute(stmt)
        await session.commit()


async def save_user_tasks(user_id: int, title: str, description: str, priority: int, deadline: datetime):
    async with AsyncSessionLocal() as session:
        stmt = insert(Task).values(
            user_id=user_id,
            title=title,
            description=description,
            priority=priority,
            deadline=deadline
        )
        await session.execute(stmt)
        await session.commit()


async def get_active_tasks(user_id: int):
    async with AsyncSessionLocal() as session:
        stmt = select(Task).where(
            Task.user_id == user_id,
            Task.is_completed == False
        ).order_by(
            Task.priority.desc(),
            Task.deadline.asc()
        )
        result = await session.execute(stmt)
        return result.scalars().all()


async def mark_task_completed(task_id: int):
    async with AsyncSessionLocal() as session:
        stmt = update(Task).where(
            Task.id == task_id
        ).values(
            is_completed=True
        )
        await session.execute(stmt)
        await session.commit()


async def delete_task(task_id: int):
    async with AsyncSessionLocal() as session:
        stmt = delete(Task).where(
            Task.id == task_id
        )
        await session.execute(stmt)
        await session.commit()


async def update_task_field(task_id: int, field: str, new_value: str | datetime):
    async with AsyncSessionLocal() as session:
        stmt = update(Task).where(
            Task.id == task_id
        ).values(**{field: new_value})
        await session.execute(stmt)
        await session.commit()


async def get_upcoming_deadlines(min_minutes: int, max_minutes: int):
    now = datetime.now(ZoneInfo("Asia/Almaty"))
    start = now + timedelta(minutes=min_minutes)
    end = now + timedelta(minutes=max_minutes)

    async with AsyncSessionLocal() as session:
        stmt = select(Task).where(
            Task.is_completed == False,
            Task.deadline > start,
            Task.deadline <= end
        )
        result = await session.execute(stmt)
        return result.scalars().all()


async def get_user_profile_stats(user_id: int) -> dict | None:
    async with AsyncSessionLocal() as session:
        user_stmt = select(User).where(User.user_tg_id == user_id)
        user = (await session.execute(user_stmt)).scalar_one_or_none()

        if not user:
            return None

        tasks_stmt = select(Task.is_completed).where(Task.user_id == user_id)
        tasks_status = (await session.execute(tasks_stmt)).scalars().all()

        total_tasks = len(tasks_status)
        completed_tasks = sum(1 for status in tasks_status if status is True)
        active_tasks = total_tasks - completed_tasks

        return {
            "username": user.username,
            "created_at": user.created_at,
            "total": total_tasks,
            "completed": completed_tasks,
            "active": active_tasks
        }
