from typing import Literal

from dishka import Provider, Scope, provide
from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvConfig(BaseSettings):
    """Runtime config populated from process env vars, with `.env` as fallback.

    Field names map 1:1 to the env var names.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    DISCORD_TOKEN: str
    DATABASE_URL: str
    GUILD_ID: int
    BOT_CHANNEL_ID: int
    GITHUB_SHA: str = "dev"
    ENVIRONMENT: Literal["dev", "prod"] = "dev"


class ConfigProvider(Provider):
    @provide(scope=Scope.APP)
    def get_env(self) -> EnvConfig:
        # model_validate({}) pulls values from env/.env like EnvConfig(),
        # but keeps basedpyright/mypy/ty happy without ignores.
        return EnvConfig.model_validate({})
