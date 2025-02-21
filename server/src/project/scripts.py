def run_tg_bot():
    from backend import init_db
    from tg_bot import run_bot

    init_db()
    run_bot()


def run_fastapi():
    import os
    import sys

    from . import settings
    from .env import granian_settings

    (settings.BASE_DIR / "logs").mkdir(exist_ok=True)

    os.execvp(
        "granian",
        [
            "granian",
            "backend.app:app",
            "--reload",
            "--interface",
            "asgi",
            "--workers",
            str(granian_settings.workers),
            "--host",
            granian_settings.host,
            "--port",
            str(granian_settings.port),
            *sys.argv[2:],
        ],
    )


def serve_fastapi():
    import os
    import sys

    from . import settings
    from .env import granian_settings

    (settings.BASE_DIR / "logs").mkdir(exist_ok=True)

    os.execvp(
        "granian",
        [
            "granian",
            "backend.app:app",
            "--interface",
            "asgi",
            "--workers",
            str(granian_settings.workers),
            "--host",
            granian_settings.host,
            "--port",
            str(granian_settings.port),
            "--log-config",
            "src/conf/logconfig.json",
            "--access-log",
            *sys.argv[2:],
        ],
    )
