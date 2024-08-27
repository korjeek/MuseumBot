from dotenv import load_dotenv
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy import String, BigInteger, ForeignKey, Column, URL
import os

load_dotenv()
postgres_url = URL.create(
    "postgresql+asyncpg",
    username=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    host=os.getenv('POSTGRES_HOST'),
    database=os.getenv('POSTGRES_DB'),
    port=os.getenv('POSTGRES_PORT')
)

engine = create_async_engine(url=postgres_url)
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, unique=True)


class Museum(Base):
    __tablename__ = 'museums'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(80))
    category: Mapped[int] = mapped_column(ForeignKey('categories.id'))
    latitude: Mapped[str] = mapped_column(String(10))
    longitude: Mapped[str] = mapped_column(String(10))
    site: Mapped[str] = mapped_column(String(110))
    request_site: Mapped[str] = mapped_column(String(120))


class Category(Base):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(20))


class Favorite(Base):
    __tablename__ = 'favorite'

    id: Mapped[int] = mapped_column(primary_key=True)
    user: Mapped[int] = mapped_column(ForeignKey('users.id'))
    museum: Mapped[int] = mapped_column(ForeignKey('museums.id'))


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
