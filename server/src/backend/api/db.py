from tortoise import Tortoise, run_async

# from aioredis import
from project import settings


async def _init():
    await Tortoise.init(config=settings.TORTOISE_ORM)
    # Generate the schema
    # await Tortoise.generate_schemas()


def init_db():
    run_async(_init())
