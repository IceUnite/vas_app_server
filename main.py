import base64
from contextlib import asynccontextmanager
from sqlite3 import IntegrityError
from typing import Optional, List

from fastapi import FastAPI, Depends, Form, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Enum, select
import enum

# Определение перечисления для статуса документа
class DocumentStatus(enum.Enum):
    READY = "готов"
    CANCELED = "отменён"
    COMPLETED = "выполнен"
    IN_PROGRESS = "в работе"

# Настройка базы данных
DATABASE_URL = 'sqlite+aiosqlite:///tasks.db'
engine = create_async_engine(DATABASE_URL, echo=True)
new_session = async_sessionmaker(engine, expire_on_commit=False)

class Model(DeclarativeBase):
    pass

# Модель ORM для задач
class TasksOrm(Model):
    __tablename__ = 'tasks'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()

# Модель ORM для документов
class DocumentsOrm(Model):
    __tablename__ = 'documents'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()
    status: Mapped[DocumentStatus] = mapped_column(Enum(DocumentStatus))

# Управление таблицами
async def create_table():
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)

async def delete_table():
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.drop_all)

# Настройка приложения FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    print(Model.metadata)
    await delete_table()
    await create_table()
    yield

app = FastAPI(lifespan=lifespan)

# Зависимость для получения сессии
async def get_session() -> AsyncSession:
    async with new_session() as session:
        yield session

# Модели Pydantic
class DocumentBase(BaseModel):
    name: str
    description: str
    status: DocumentStatus

class Document(DocumentBase):
    id: int

    class Config:
        from_attributes = True

class STaskAdd(BaseModel):
    name: str
    description: Optional[str] = None

class STask(STaskAdd):
    id: int

    class Config:
        from_attributes = True

# Эндпоинт для добавления задачи
@app.post('/post_tasks', response_model=STask)
async def add_task(
    name: str = Form(..., description="Название задачи"),
    description: str = Form(None, description="Описание задачи (опционально)"),
    session: AsyncSession = Depends(get_session),
):
    new_task = TasksOrm(name=name, description=description)
    session.add(new_task)
    await session.commit()
    await session.refresh(new_task)
    return new_task

# Эндпоинт для получения всех задач
@app.get('/tasks', response_model=List[STask])
async def get_tasks(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(TasksOrm))
    tasks = result.scalars().all()
    return tasks

# Эндпоинт для создания документа
@app.post('/documents', response_model=Document)
async def create_document(
    name: str = Form(..., description="Название документа"),
    description: str = Form('Описание документа Описание документа Описание документа Описание документа Описание документа Описание документа Описание документа Описание документа Описание документа Описание документа Описание документа Описание документа ', description="Описание документа"),
    status: DocumentStatus = Form(..., description="Статус документа"),
    session: AsyncSession = Depends(get_session),
):
    new_document = DocumentsOrm(
        name=name,
        description=description,
        status=status
    )
    session.add(new_document)
    try:
        await session.commit()
        await session.refresh(new_document)
        return new_document
    except IntegrityError as e:
        print(f"Ошибка базы данных: {e}")
        await session.rollback()
        raise HTTPException(status_code=400, detail="Ошибка создания документа")
    except Exception as e:
        print(f"Неизвестная ошибка: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

# Эндпоинт для получения всех документов
@app.get('/documents', response_model=List[Document])
async def get_documents(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(DocumentsOrm))
    documents = result.scalars().all()
    return documents

# Эндпоинт для удаления документа
@app.delete('/documents/{document_id}', response_model=dict)
async def delete_document(document_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(DocumentsOrm).where(DocumentsOrm.id == document_id))
    document = result.scalar_one_or_none()
    if not document:
        raise HTTPException(status_code=404, detail="Документ не найден")

    await session.delete(document)
    await session.commit()
    return {"message": f"Документ с ID {document_id} успешно удален"}
