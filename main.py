from aiogram import Bot, Dispatcher
from app.database.models import create_tables
from app.handlers import router
from dotenv import load_dotenv
import asyncio
import os

load_dotenv()
bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher()


async def main():
    dp.include_router(router)
    await create_tables()
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Shutdown...')
