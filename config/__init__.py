import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class CommonSettings(BaseSettings):
    APP_NAME: str = os.getenv("APP_NAME")
    DEBUG_MODE: bool = os.getenv("DEBUG_MODE")


class ServerSettings(BaseSettings):
    HOST: str = os.getenv("HOST")
    PORT: int = os.getenv("PORT")


class DatabaseSettings(BaseSettings):
    DB_URL: str = os.getenv("DB_URL")
    DB_NAME: str = os.getenv("DB_NAME")


class Settings(CommonSettings, ServerSettings, DatabaseSettings):
    pass


settings = Settings()