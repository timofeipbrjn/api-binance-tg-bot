import asyncio
import asyncpg
import os
import aiohttp

from redis.asyncio import Redis
from aiogram.fsm.storage.redis import RedisStorage
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from app.handlers import router as main_router
from services.api_client import CurrencyApiClient

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
DB_URL = os.getenv('DATABASE_URL')

async def main():
    redis_client = Redis(host="localhost", port=6379, decode_responses=True)
    storage = RedisStorage(redis=redis_client)
    db_pool = await asyncpg.create_pool(DB_URL)

    session = aiohttp.ClientSession()

    bot = Bot(token=TOKEN)
    dp = Dispatcher(storage=storage)

    binance_client = CurrencyApiClient('https://api.binance.com/api/v3/ticker/price', session)

    dp["db_pool"] = db_pool
    dp["client"] = binance_client

    dp.include_router(main_router)

    try:
        print("ready to func")

        await bot.delete_webhook(drop_pending_updates=True)

        await dp.start_polling(bot)

    finally:
        print("OFFING")
        await redis_client.close()
        await db_pool.close()
        await binance_client.close()
        print("OFFED")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")
