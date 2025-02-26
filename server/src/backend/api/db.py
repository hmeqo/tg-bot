# from aioredis import
from project import settings
from redis import asyncio as aioredis
from tortoise import Tortoise, run_async

redis_client = aioredis.from_url("redis://localhost:6379/1", decode_responses=True)


async def _init():
    await Tortoise.init(config=settings.TORTOISE_ORM)
    # Generate the schema
    # await Tortoise.generate_schemas()


def init_db():
    run_async(_init())
