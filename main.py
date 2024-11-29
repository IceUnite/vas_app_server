from contextlib import asynccontextmanager
from sqlalchemy.future import select
from typing import Optional
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from database import create_table, delete_table, new_session, TasksOrm, Model


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(Model.metadata)
    # await delete_table()  # Удаление таблиц перед запуском приложения
    await create_table()  # Создание таблиц
    print("Database Ready")

    yield  # Запускаем приложение

    print("Application Shutdown")


app = FastAPI(lifespan=lifespan)


async def get_session() -> AsyncSession:
    async with new_session() as session:
        yield session


class STaskAdd(BaseModel):
    name: str
    description: Optional[str] = None


class STask(STaskAdd):
    id: int

    class Config:
        from_attributes = True



@app.post('/post_tasks', response_model=STask)
async def add_task(task: STaskAdd, session: AsyncSession = Depends(get_session)):
    new_task = TasksOrm(name=task.name, description=task.description)
    session.add(new_task)
    await session.commit()
    await session.refresh(new_task)
    return new_task

@app.get('/tasks', response_model=list[STask])
async def get_tasks(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(TasksOrm))
    tasks = result.scalars().all()
    return tasks
