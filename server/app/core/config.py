import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL", "postgresql+psycopg://postgres:mame33@localhost:5432/test")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")

settings = Settings()