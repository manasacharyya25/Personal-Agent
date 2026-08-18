import os
import asyncpg
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.host = os.getenv("DB_HOST")
        self.port = int(os.getenv("DB_PORT", "5432"))
        self.database = os.getenv("DB_NAME")
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")

        self.min_pool_size = int(os.getenv("DB_MIN_POOL_SIZE", "5"))
        self.max_pool_size = int(os.getenv("DB_MAX_POOL_SIZE", "20"))

    async def connect(self):
        self.pool = await asyncpg.create_pool(
            host=self.host,
            port=self.port,
            database=self.database,
            user=self.user,
            password=self.password,
            min_size=self.min_pool_size,
            max_size=self.max_pool_size,
        )

    async def close(self):
        if self.pool:
            await self.pool.close()

    async def fetch(self, query: str, *args):
        return await self.pool.fetch(query, *args)

    async def fetchrow(self, query: str, *args):
        return await self.pool.fetchrow(query, *args)

    async def execute(self, query: str, *args):
        return await self.pool.execute(query, *args)