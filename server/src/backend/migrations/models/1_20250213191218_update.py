from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "tgbot_daily_session" ALTER COLUMN "in_fee_rate" SET DEFAULT 0;
        ALTER TABLE "tgbot_daily_session" ALTER COLUMN "out_fee_rate" SET DEFAULT 0;
        ALTER TABLE "tgbot_daily_session" ALTER COLUMN "in_exchange_rate" SET DEFAULT 1;
        ALTER TABLE "tgbot_daily_session" ALTER COLUMN "out_exchange_rate" SET DEFAULT 1;
        ALTER TABLE "tgbot_transaction" ALTER COLUMN "type" TYPE VARCHAR(6) USING "type"::VARCHAR(6);
        COMMENT ON COLUMN "tgbot_transaction"."type" IS 'INCOME: income
PAYOUT: payout';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        COMMENT ON COLUMN "tgbot_transaction"."type" IS 'INCOME: income
PAYOUT: payout
CORRECTION: correction';
        ALTER TABLE "tgbot_transaction" ALTER COLUMN "type" TYPE VARCHAR(10) USING "type"::VARCHAR(10);
        ALTER TABLE "tgbot_daily_session" ALTER COLUMN "in_fee_rate" DROP DEFAULT;
        ALTER TABLE "tgbot_daily_session" ALTER COLUMN "out_fee_rate" DROP DEFAULT;
        ALTER TABLE "tgbot_daily_session" ALTER COLUMN "in_exchange_rate" DROP DEFAULT;
        ALTER TABLE "tgbot_daily_session" ALTER COLUMN "out_exchange_rate" DROP DEFAULT;"""
