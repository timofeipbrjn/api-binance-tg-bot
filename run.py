import asyncio
import os
import aiohttp
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from app.handlers import router
from services.api_client import CurrencyApiClient

load_dotenv()

TOKEN = os.environ.get('BOT_TOKEN')
if not TOKEN:
    raise ValueError("Токен не указан")

bot = Bot(token=TOKEN)
dp = Dispatcher()

async def main():
    async with aiohttp.ClientSession() as session:
        client = CurrencyApiClient('https://api.binance.com/api/v3/ticker/price', session)

        dp['client'] = client

        print("Бот запущен")
        dp.include_router(router)
        await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")
