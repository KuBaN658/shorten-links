from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel


class DatabaseConfig(BaseModel):
    host: str
    port: str
    user: str
    name: str
    password: str


class AccessToken(BaseModel):
    lifetime_seconds: int = 3600
    reset_password_token_secret: str
    verification_token_secret: str


class LifeTimeLinks(BaseModel):
    without_clicks: int = 60
    default_with_clicks: int = 60 * 5


class RedisConfig(BaseModel):
    cache_host: str
    tasks_host: str


class Settings(BaseSettings):
    db: DatabaseConfig
    access_token: AccessToken
    life_time_links: LifeTimeLinks = LifeTimeLinks()
    redis: RedisConfig

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
    )


settings = Settings()
