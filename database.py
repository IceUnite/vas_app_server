from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Enum

import enum

from constants.consts import DocumentStatus

engine = create_async_engine('sqlite+aiosqlite:///tasks.db', echo=True)
new_session = async_sessionmaker(engine, expire_on_commit=False)


class Model(DeclarativeBase):
    pass


class TasksOrm(Model):
    __tablename__ = 'tasks'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()




# Модель для документов
class DocumentsOrm(Model):
    __tablename__ = 'documents'
    id: Mapped[int] = mapped_column(primary_key=True)  # Уникальный идентификатор
    name: Mapped[str] = mapped_column()  # Название документа
    description: Mapped[str] = mapped_column()  # Описание документа
    status: Mapped[DocumentStatus] = mapped_column(Enum(DocumentStatus))  # Статус документа
    # file_path: Mapped[str] = mapped_column()  # Путь к файлу документа (например, Word)





async def create_table():
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)


async def delete_table():
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.drop_all)
