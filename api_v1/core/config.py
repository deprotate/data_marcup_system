import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    secret: str = 'MR.PENIS'
    SECRET: str = secret
    db_user: str = 'postgres'
    db_password: str = 'admin'
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "data_marcup_system_db"

    @property
    def db_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.db_user}:"
            f"{self.db_password}@{self.db_host}:"
            f"{self.db_port}/{self.db_name}"
        )

    class Config:
        env_file = "../../.env"
        env_file_encoding = "utf-8"

settings = Settings()
