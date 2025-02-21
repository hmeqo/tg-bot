from pydantic_settings import BaseSettings, SettingsConfigDict


class TgBotSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="BOT_")

    token: str = ""


class GranianSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="GRANIAN_")

    workers: int = 2
    host: str = "::"
    port: int = 8000


class WebSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="WEB_")

    url: str = "http://localhost:3000"


bot_settings = TgBotSettings()

granian_settings = GranianSettings()

web_settings = WebSettings()
