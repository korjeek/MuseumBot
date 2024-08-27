from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

import app.database.requests as request


class KeyboardData:
    def __init__(self, favourite_callback: str,  # CallbackData для кнопки 'Избранное'
                 favorite_btn_text: str,  # Название кнопки 'Избранное'
                 url: str,  # URL для кнопки 'Сайт'
                 museum_callback: str | None = None,  # CallbackData для кнопки
                 nxt_btn_text: str | None = None) -> None:  # Название кнопки меняющей страницу
        self.museum_callback = museum_callback
        self.favourite_callback = favourite_callback
        self.nxt_btn_text = nxt_btn_text
        self.favorite_btn_text = favorite_btn_text
        self.url = url


class Keyboard:
    @staticmethod
    async def categories() -> InlineKeyboardMarkup:
        categories = await request.get_categories()
        keyboard = InlineKeyboardBuilder()

        for ctg in categories:
            callback_data = CategoryCallback(category=ctg.id, page=1).pack()
            keyboard.add(InlineKeyboardButton(text=ctg.name, callback_data=callback_data))
        return keyboard.adjust(3).as_markup()

    @staticmethod
    async def normal_museum_kbd(kbd_data: KeyboardData) -> InlineKeyboardMarkup:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Сайт', url=kbd_data.url)],
            [InlineKeyboardButton(text=kbd_data.favorite_btn_text, callback_data=kbd_data.favourite_callback)],
            [InlineKeyboardButton(text=kbd_data.nxt_btn_text, callback_data=kbd_data.museum_callback)]
        ])

        return keyboard

    @staticmethod
    async def small_museum_kbd(kbd_data: KeyboardData) -> InlineKeyboardMarkup:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Сайт', url=kbd_data.url)],
            [InlineKeyboardButton(text=kbd_data.favorite_btn_text, callback_data=kbd_data.favourite_callback)]
        ])

        return keyboard

    @staticmethod
    async def location_kbd() -> ReplyKeyboardMarkup:
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
            [KeyboardButton(text='Отправить геопозицию 🌎', request_location=True)]
        ])

        return keyboard


# =====================================Callback-Фабрика====================================
class CategoryCallback(CallbackData, prefix='category'):
    category: int  # Категория музея
    museum: int | None = None  # ID музея в БД
    page: int  # Страница выбора музея
    change_favorite_state: bool = False  # Было ли изменено состояние музея на 'избранное / не избранное'
    close: bool = False  # Необходимо ли закрыть текущее меню


class RandomCallback(CallbackData, prefix='random'):
    museum: int  # ID музея в БД
    change_favorite_state: bool = False  # Было ли изменено состояние музея на 'избранное / не избранное'


class LocalCallback(CallbackData, prefix='local'):
    latitude: float  # Широта
    longitude: float  # Долгота
    museum: int | None = None  # ID музея в БД
    page: int  # Страница выбора музея
    change_favorite_state: bool = False  # Было ли изменено состояние музея на 'избранное / не избранное'


class FavoriteCallback(CallbackData, prefix='favorite'):
    museum: int | None = None  # ID музея в БД
    page: int  # Страница выбора музея
    change_favorite_state: bool = False  # Было ли изменено состояние музея на 'избранное / не избранное'
