from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);
CREATE TABLE IF NOT EXISTS "tgbot_group" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "chat_id" BIGINT NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON COLUMN "tgbot_group"."chat_id" IS '群组ID';
CREATE TABLE IF NOT EXISTS "tgbot_daily_session" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "started_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "in_fee_rate" DECIMAL(10,4) NOT NULL DEFAULT 0,
    "in_exchange_rate" DECIMAL(10,2) NOT NULL DEFAULT 1,
    "out_fee_rate" DECIMAL(10,4) NOT NULL DEFAULT 0,
    "out_exchange_rate" DECIMAL(10,2) NOT NULL DEFAULT 1,
    "group_id" BIGINT NOT NULL REFERENCES "tgbot_group" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "tgbot_daily_session"."started_at" IS '开始时间';
CREATE TABLE IF NOT EXISTS "tgbot_user" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "chat_id" BIGINT,
    "username" VARCHAR(255),
    "joined_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON COLUMN "tgbot_user"."chat_id" IS '用户ID';
COMMENT ON COLUMN "tgbot_user"."username" IS '用户名';
COMMENT ON COLUMN "tgbot_user"."joined_at" IS '加入时间';
CREATE TABLE IF NOT EXISTS "tgbot_group_operator" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "added_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "group_id" BIGINT NOT NULL REFERENCES "tgbot_group" ("id") ON DELETE CASCADE,
    "user_id" BIGINT NOT NULL REFERENCES "tgbot_user" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_tgbot_group_group_i_3926f9" UNIQUE ("group_id", "user_id")
);
CREATE TABLE IF NOT EXISTS "tgbot_transaction" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "type" VARCHAR(6) NOT NULL,
    "currency" VARCHAR(4) NOT NULL DEFAULT 'CNY',
    "amount" DECIMAL(15,2) NOT NULL,
    "fee_rate" DECIMAL(10,4) NOT NULL,
    "exchange_rate" DECIMAL(10,4) NOT NULL,
    "is_correction" BOOL NOT NULL DEFAULT False,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "operator_id" BIGINT REFERENCES "tgbot_user" ("id") ON DELETE SET NULL,
    "session_id" BIGINT NOT NULL REFERENCES "tgbot_daily_session" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "tgbot_transaction"."type" IS '入款: income\n下发: payout';
COMMENT ON COLUMN "tgbot_transaction"."currency" IS '人民币: CNY\nUSDT: USDT';
COMMENT ON COLUMN "tgbot_transaction"."amount" IS '金额';
COMMENT ON COLUMN "tgbot_transaction"."is_correction" IS '修正记录';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
