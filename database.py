from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

engine = create_async_engine('sqlite+aiosqlite:///tasks.db', echo=True)
new_session = async_sessionmaker(engine, expire_on_commit=False)


class Model(DeclarativeBase):
    pass


class TasksOrm(Model):
    __tablename__ = 'tasks'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()


async def create_table():
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)


async def delete_table():
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.drop_all)
