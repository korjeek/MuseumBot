from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, ContentType, ReplyKeyboardRemove
from app.messages.keyboards import Keyboard, CategoryCallback, RandomCallback, LocalCallback, FavoriteCallback
from app.messages import text
from app.database.requests import change_favorite, set_user
from app.messages.creator import Creator
from random import randint

router = Router()
kbd = Keyboard()
creator = Creator()


# ========================================Команды==========================================
@router.message(CommandStart())
async def start(message: Message):
    await set_user(message.from_user.id)
    await message.answer(text=text.START_MESSAGE)


@router.message(Command('choose'))
async def choose(message: Message):
    await message.answer(text=text.CHOOSE_MESSAGE, reply_markup=await kbd.categories())


@router.message(Command('random'))
async def random(message: Message):
    keyboard, museum_data = await creator.random_museum_msg(message.from_user.id, randint(1, 37))
    await message.answer(text=museum_data, reply_markup=keyboard, parse_mode='html')


@router.message(Command('locate'))
async def locate(message: Message):
    await message.answer(text=text.LOCATION_REQ_MESSAGE, reply_markup=await kbd.location_kbd())


@router.message(Command('favorites'))
async def favorites(message: Message):
    keyboard, museum_data = await creator.favorite_museum_msg(FavoriteCallback(page=1), message.from_user.id)

    if keyboard is None:
        await message.answer(text=text.FAVORITE_EMPTY_MESSAGE)
    else:
        await message.answer(text=museum_data, reply_markup=keyboard, parse_mode='html')


# ==================================Callback-Обработчики===================================
@router.callback_query(CategoryCallback.filter())
async def category_callback_query(call: CallbackQuery, callback_data: CategoryCallback) -> None:
    # Нужно ли изменить состояние музея на 'избранное / не избранное'
    if callback_data.change_favorite_state:
        await change_favorite(call.from_user.id, callback_data.museum)
    # Нужно ли вернуться в начальное меню
    if callback_data.close:
        await call.message.edit_text(text=text.CHOOSE_MESSAGE, reply_markup=await kbd.categories())
    # Иначе, создание новой страницы музея
    else:
        keyboard, museum_data = await creator.category_museum_msg(callback_data, call.from_user.id)
        await call.message.edit_text(text=museum_data, reply_markup=keyboard, parse_mode='html')


@router.callback_query(RandomCallback.filter())
async def back_callback_query(call: CallbackQuery, callback_data: CategoryCallback) -> None:
    # Нужно ли изменить состояние музея на 'избранное / не избранное'
    if callback_data.change_favorite_state:
        await change_favorite(call.from_user.id, callback_data.museum)

    # Создание новой страницы музея
    keyboard, museum_data = await creator.random_museum_msg(call.from_user.id, callback_data.museum)
    await call.message.edit_text(text=museum_data, reply_markup=keyboard, parse_mode='html')


@router.message(F.content_type == ContentType.LOCATION)
async def locate_museums(message: Message):
    # Удаление кнопки 'запроса'
    await message.answer(text=text.LOCATE_MESSAGE, reply_markup=ReplyKeyboardRemove())

    # Создание новой страницы музея
    callback_data = LocalCallback(latitude=message.location.latitude, longitude=message.location.longitude, page=1)
    keyboard, museum_data = await creator.local_museum_msg(callback_data, message.from_user.id)
    await message.answer(text=museum_data, reply_markup=keyboard, parse_mode='html')


@router.callback_query(LocalCallback.filter())
async def geo_callback_query(call: CallbackQuery, callback_data: LocalCallback):
    # Нужно ли изменить состояние музея на 'избранное / не избранное'
    if callback_data.change_favorite_state:
        await change_favorite(call.from_user.id, callback_data.museum)

    # Создание новой страницы музея
    keyboard, museum_data = await creator.local_museum_msg(callback_data, call.from_user.id)
    await call.message.edit_text(text=museum_data, reply_markup=keyboard, parse_mode='html')


@router.callback_query(FavoriteCallback.filter())
async def favorite_callback_query(call: CallbackQuery, callback_data: FavoriteCallback):
    # Нужно ли изменить состояние музея на 'избранное / не избранное'
    if callback_data.change_favorite_state:
        await change_favorite(call.from_user.id, callback_data.museum)

    # Создание новой страницы музея
    keyboard, museum_data = await creator.favorite_museum_msg(callback_data, call.from_user.id)

    if keyboard is None:
        await call.message.edit_text(text=text.FAVORITE_EMPTY_MESSAGE)
    else:
        await call.message.edit_text(text=museum_data, reply_markup=keyboard, parse_mode='html')
