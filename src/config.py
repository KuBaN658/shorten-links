from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel


class DatabaseConfig(BaseModel):
    host: str
    port: str
    user: str
    name: str
    password: str


class AccessToken(BaseModel):
    lifetime_seconds: str = 3600
    reset_password_token_secret: str
    verification_token_secret: str


class Settings(BaseSettings):
    db: DatabaseConfig
    access_token: AccessToken

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
    )


settings = Settings()
