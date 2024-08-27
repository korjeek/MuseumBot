from app.database.models import async_session, Category, Museum, Favorite, User
from sqlalchemy import select
from geopy.distance import geodesic


# =======================================Пользователи======================================
async def set_user(user_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.user_id == user_id))

        if not user:
            session.add(User(user_id=user_id))
            await session.commit()


async def get_user_id(user_id):
    async with async_session() as session:
        return await session.scalar(select(User.id).where(User.user_id == user_id))


# ========================================Категории========================================
async def get_categories():
    async with async_session() as session:
        return await session.scalars(select(Category))


async def get_category_name(category_id: int):
    async with async_session() as session:
        category_name = await session.scalar(select(Category).where(Category.id == category_id))
        return category_name.name


# ==========================================Музеи==========================================
async def get_museums(category_id: int):
    async with async_session() as session:
        return await session.scalars(select(Museum).where(Museum.category == category_id))


async def get_museum(museum_id):
    async with async_session() as session:
        return await session.scalar(select(Museum).where(Museum.id == museum_id))


async def get_local_museums(user_location: tuple[float, float]):
    async with async_session() as session:
        museums = list(await session.scalars(select(Museum)))
        museums.sort(key=lambda museum: get_distance(user_location, (museum.latitude, museum.longitude)))
        return museums[:3]


def get_distance(user_location: tuple[float, float], museum_location: tuple[float, float]) -> float:
    return geodesic(museum_location, user_location).meters


# ========================================Избранное========================================
async def check_favorite(user_id: int, museum: int):
    async with async_session() as session:
        user = await get_user_id(user_id)
        favorite = await session.scalar(select(Favorite).where(Favorite.museum == museum and Favorite.user == user))
        return True if favorite else False


async def change_favorite(user_id: int, museum: int):
    async with async_session() as session:
        user = await get_user_id(user_id)
        favorite = await session.scalar(select(Favorite).where(Favorite.museum == museum and Favorite.user == user))

        if not favorite:
            session.add(Favorite(user=user, museum=museum))
        else:
            await session.delete(favorite)
        await session.commit()


async def get_favorite_museums(user_id: int):
    async with async_session() as session:
        user = await get_user_id(user_id)
        favorite_museums = await session.scalars(select(Favorite.museum).where(Favorite.user == user))

        return [await get_museum(museum_id) for museum_id in favorite_museums]
