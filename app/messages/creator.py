from aiogram.types import InlineKeyboardMarkup
from app.requests.data import get_museum_data
from app.messages.keyboards import CategoryCallback, Keyboard, KeyboardData, RandomCallback, LocalCallback, \
    FavoriteCallback

from app.paginator import Paginator
import app.database.requests as request


class Creator:
    def __init__(self):
        self.kbd = Keyboard()

    async def category_museum_msg(self, callback: CategoryCallback, user_id: int) -> tuple[InlineKeyboardMarkup, str]:
        # Получаем список музеев, принадлежащих данной категории
        museums = list(await request.get_museums(callback.category))

        # Используем пагинатор
        paginator = Paginator(museums, page=callback.page)
        museum = paginator.get_page()[0]

        # Получаем название кнопок
        nxt_btn_text, close = await self.choose_nxt_btn(paginator)
        favorite_btn_text = await self.choose_favorite_btn(await request.check_favorite(user_id, museum.id))

        # Создаем CallbackData
        category_callback = CategoryCallback(
            category=callback.category,
            page=callback.page + 1,
            museum=museum.id,
            close=close
        ).pack()
        favorite_callback = CategoryCallback(
            category=callback.category,
            page=callback.page,
            museum=museum.id,
            change_favorite_state=True
        ).pack()

        # Создаем KeyboardData
        kbd_data = KeyboardData(
            museum_callback=category_callback,
            favourite_callback=favorite_callback,
            nxt_btn_text=nxt_btn_text,
            favorite_btn_text=favorite_btn_text,
            url=museum.request_site
        )

        # Получаем клавиатуру и информацию о музее для страницы
        keyboard = await self.kbd.normal_museum_kbd(kbd_data)
        category_name = await request.get_category_name(callback.category)
        museum_data = await get_museum_data(museum.name, category_name, museum.request_site)

        return keyboard, museum_data

    async def random_museum_msg(self, user_id: int, museum_id: int) -> tuple[InlineKeyboardMarkup, str]:
        # Получаем рандомный музей
        museum = await request.get_museum(museum_id)

        # Получаем название кнопок
        favorite_btn_text = await self.choose_favorite_btn(await request.check_favorite(user_id, museum.id))

        # Создаем CallbackData
        favorite_callback = RandomCallback(museum=museum.id, change_favorite_state=True).pack()

        # Создаем KeyboardData
        kbd_data = KeyboardData(
            favourite_callback=favorite_callback,
            favorite_btn_text=favorite_btn_text,
            url=museum.request_site
        )

        # Получаем клавиатуру и информацию о музее для страницы
        keyboard = await self.kbd.small_museum_kbd(kbd_data)
        category_name = await request.get_category_name(museum.category)
        museum_data = await get_museum_data(museum.name, category_name, museum.request_site)

        return keyboard, museum_data

    async def local_museum_msg(self, callback: LocalCallback, user_id: int):
        # Получаем список ближайших музеев
        museums = await request.get_local_museums((callback.latitude, callback.longitude))

        # Используем пагинатор
        paginator = Paginator(museums, page=callback.page)
        museum = paginator.get_page()[0]

        # Получаем название кнопок
        favorite_btn_text = await self.choose_favorite_btn(await request.check_favorite(user_id, museum.id))

        # Создаем CallbackData
        local_callback = LocalCallback(
            latitude=callback.latitude,
            longitude=callback.longitude,
            page=callback.page + 1,
            museum=museum.id,
        ).pack()
        favorite_callback = LocalCallback(
            latitude=callback.latitude,
            longitude=callback.longitude,
            page=callback.page,
            museum=museum.id,
            change_favorite_state=True
        ).pack()

        # Создаем KeyboardData
        kbd_data = KeyboardData(
            museum_callback=local_callback,
            favourite_callback=favorite_callback,
            nxt_btn_text='Следующий музей',
            favorite_btn_text=favorite_btn_text,
            url=museum.request_site
        )

        # Получаем клавиатуру и информацию о музее для страницы
        if callback.page < 3:
            keyboard = await self.kbd.normal_museum_kbd(kbd_data)
        else:
            keyboard = await self.kbd.small_museum_kbd(kbd_data)
        category_name = await request.get_category_name(museum.category)
        museum_data = await get_museum_data(museum.name, category_name, museum.request_site)

        return keyboard, museum_data

    async def favorite_museum_msg(self, callback: FavoriteCallback, user_id: int):
        # Получаем список избранных музеев
        museums = await request.get_favorite_museums(user_id)
        page = callback.page if callback.page >= 1 else 1

        # Дополнительный переключатель страниц в случае исключений
        if len(museums) == 0:
            return None, None

        # Используем пагинатор
        paginator = Paginator(museums, page=page)
        museum = paginator.get_page()[0]

        # Получаем название кнопок
        favorite_btn_text = await self.choose_favorite_btn(await request.check_favorite(user_id, museum.id))

        # Создаем CallbackData
        local_callback = FavoriteCallback(
            museum=museum.id,
            page=page + 1,
        ).pack()
        favorite_callback = FavoriteCallback(
            museum=museum.id,
            page=page - 1,
            change_favorite_state=True
        ).pack()

        # Создаем KeyboardData
        kbd_data = KeyboardData(
            museum_callback=local_callback,
            favourite_callback=favorite_callback,
            nxt_btn_text='Следующий музей',
            favorite_btn_text=favorite_btn_text,
            url=museum.request_site
        )

        # Получаем клавиатуру и информацию о музее для страницы
        if paginator.has_next():
            keyboard = await self.kbd.normal_museum_kbd(kbd_data)
        else:
            keyboard = await self.kbd.small_museum_kbd(kbd_data)
        category_name = await request.get_category_name(museum.category)
        museum_data = await get_museum_data(museum.name, category_name, museum.request_site)

        return keyboard, museum_data

    @staticmethod
    async def choose_nxt_btn(paginator: Paginator) -> tuple[str, bool]:
        return ('Следующий музей', False) if paginator.has_next() else ('Вернуться в меню', True)

    @staticmethod
    async def choose_favorite_btn(favorite: bool) -> str:
        return 'В избранное' if not favorite else 'Убрать из избранного'
