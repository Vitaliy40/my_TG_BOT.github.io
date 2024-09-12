from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy import BigInteger, String, ForeignKey, LargeBinary

engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3')
async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger)

class Category(Base):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(70))

class User_Info(Base):
    __tablename__ = 'users_info'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(70))
    user_cart_number: Mapped[int] = mapped_column()
    tg_id: Mapped[int] = mapped_column(BigInteger)


class Item(Base):
    __tablename__ = 'items'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(100))
    price: Mapped[int] = mapped_column()
    item_photo: Mapped[bytes] = mapped_column(LargeBinary)
    category: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    tg_id: Mapped[int] = mapped_column(BigInteger)



async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


