import asyncio
import asyncpg


async def init_db(pool: asyncpg.Pool):
    with open("services/init_db.sql", "r") as f:
        sql = f.read()

    async with pool.acquire() as conn:
        await conn.execute(sql)
    print("DB INITED")
