from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "tgbot_transaction" ALTER COLUMN "session_id" TYPE BIGINT USING "session_id"::BIGINT;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "tgbot_transaction" ALTER COLUMN "session_id" TYPE INT USING "session_id"::INT;"""
