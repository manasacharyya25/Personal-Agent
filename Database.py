import os
import asyncpg
from dotenv import load_dotenv
import psycopg2

load_dotenv()

class Database:
    def __init__(self):
        self.pool = None
        self.connection = None
        self.host = os.getenv("DB_HOST")
        self.port = int(os.getenv("DB_PORT", "5432"))
        self.database = os.getenv("DB_NAME")
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")

        self.min_pool_size = int(os.getenv("DB_MIN_POOL_SIZE", "5"))
        self.max_pool_size = int(os.getenv("DB_MAX_POOL_SIZE", "20"))

    def connect(self):
        
        url = f"postgresql://postgres.risfitksxxuphkigcrnd:{self.password}@aws-0-ap-southeast-2.pooler.supabase.com:6543/postgres"
        self.connection = psycopg2.connect(url)

        # self.pool = await asyncpg.create_pool(
        #     dsn=f"postgresql://postgres.risfitksxxuphkigcrnd:{self.password}@aws-0-ap-southeast-2.pooler.supabase.com:5432/postgres",
        #     min_size=self.min_pool_size,
        #     max_size=self.max_pool_size,
        # )
        # self.pool = await asyncpg.create_pool(
        #     host=self.host,
        #     port=self.port,
        #     database=self.database,
        #     user=self.user,
        #     password=self.password,
        #     min_size=self.min_pool_size,
        #     max_size=self.max_pool_size,
        # )

    def close(self):
        if self.connection:
            self.connection.close()

    async def fetch(self, query: str, *args):
        return await self.pool.fetch(query, *args)

    async def fetchrow(self, query: str, *args):
        return await self.pool.fetchrow(query, *args)

    def execute(self, query: str, *args):
        with self.connection.cursor() as cursor:
            cursor.execute(query, args)

        self.connection.commit()

    def similarity_search(
        self,
        embedding: list[float],
        limit: int = 5
    ):
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    content,
                    source,
                    1 - (embedding <=> %s::vector) AS similarity
                FROM rhoq_info
                ORDER BY embedding <=> %s::vector
                LIMIT %s
                """,
                (embedding, embedding, limit)
            )

            return cursor.fetchall()