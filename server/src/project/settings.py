from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent

TORTOISE_ORM = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.asyncpg",
            "credentials": {
                "host": "localhost",
                "port": 5432,
                "user": "tg_bot",
                "password": "ar1234",
                "database": "tg_bot",
            },
        },
    },
    "apps": {
        "models": {
            "models": ["aerich.models", "backend.api.main.models"],
            "default_connection": "default",
        },
    },
    "use_tz": True,
    "timezone": "Asia/Shanghai",
}
