import asyncio
from models import async_main
from aiogram import Bot, Dispatcher
from handlers import router
import os
from dotenv import load_dotenv

load_dotenv()
bot = Bot(token=os.getenv('TG_TOKEN'))
API_TOKEN = os.getenv('API_TOKEN')


dp = Dispatcher()

async def main():
    dp.include_router(router)
    await async_main()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
