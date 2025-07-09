from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    DATABASE_URL: str


    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
