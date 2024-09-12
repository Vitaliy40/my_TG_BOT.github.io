from models import User, async_session, Item, User_Info, Category
from sqlalchemy.future import select
from sqlalchemy import delete


async def add_info_user_to_db(username: str, user_cart_number: str, tg_id: int):
    async with async_session() as session:
        async with session.begin():
            new_user = User_Info(
                username=username,
                user_cart_number=user_cart_number,
                tg_id=tg_id
            )
        session.add(new_user)
        await session.commit()

async def add_user_to_db(tg_id: int):
    async with async_session() as session:
        async with session.begin():
            user = User(
                tg_id=tg_id
            )
            session.add(user)
            await session.commit()


async def get_categories():
    async with async_session() as session:
        return await session.scalars(select(Category))

async def delete_all_users():
    async with async_session() as session:

        stmt = delete(User)
        await session.execute(stmt)
        await session.commit()

async def delete_all_user_info():
    async with async_session() as session:

        stmt = delete(User_Info)
        await session.execute(stmt)
        await session.commit()

async def get_category_id_by_name(category_name: str):
    async with async_session() as session:
        result = await session.execute(select(Category.id).where(Category.name == category_name))
        category_id = result.scalar_one_or_none()
        if category_id is None:
            raise ValueError(f"Category with name '{category_name}' not found")
        return category_id

async def get_item_photo_id_by_name(name):
    async with async_session() as session:
        result = await session.execute(
            select(Item.id).where(Item.name == name)
        )
        item = result.scalar_one_or_none()
        return item

async def add_info_item_to_db(name: str, description: str, price: int, category: int, item_photo: bytes, tg_id: int):
    async with async_session() as session:
        async with session.begin():
            category_exists = await session.scalar(select(Category.id).where(Category.id == category))
            if category_exists:
                new_item = Item(
                    name=name,
                    description=description,
                    price=price,
                    category=category,
                    item_photo=item_photo,
                    tg_id=tg_id
                )
                session.add(new_item)
                await session.commit()
            else:
                raise ValueError(f"Category with ID {category} does not exist")

async def get_item_photo(item_id):
    async with async_session() as session:
        item = await session.get(Item, item_id)
        return item.item_photo


async def get_username_by_tg_id(tg_id):
    async with async_session() as session:
        result = await session.execute(
            select(User_Info.username).where(User_Info.tg_id == tg_id)
        )
        username = result.scalar_one_or_none()
        return username

async def get_user_by_tg_id(tg_id):
    async with async_session() as session:
        result = await session.execute(
            select(User_Info).where(User_Info.tg_id == tg_id)
        )
        user = result.scalar_one_or_none()
        return user

async def get_number_cart_by_tg_id(tg_id):
    async with async_session() as session:
        result = await session.execute(
            select(User_Info.user_cart_number).where(User_Info.tg_id == tg_id)
        )
        user_cart_number = result.scalar_one_or_none()
        return user_cart_number

async def get_items_by_category(category_id):
    async with async_session() as session:
        result = await session.execute(select(Item).where(Item.category == category_id))
        return result.scalars().all()

async def get_tg_id_by_name(name):
    async with async_session() as session:
        result = await session.execute(
            select(Item.tg_id).where(Item.name == name)
        )
        tg_id = result.scalar_one_or_none()
        return tg_id


async def update_user_data(tg_id, new_name, new_card_number, new_user_name):
    async with async_session() as session:
        result = await session.execute(select(User_Info).where(User_Info.tg_id == tg_id))
        user = result.scalar_one_or_none()

        if user:
            user.name = new_name
            user.card_number = new_card_number
            user.username = new_user_name
            # Підтвердити зміни
            await session.commit()
        else:
            print("Користувача не знайдено")
