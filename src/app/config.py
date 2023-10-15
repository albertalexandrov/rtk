from pydantic_settings import BaseSettings
from sqlalchemy import URL


class DatabaseSettings(BaseSettings):
    class Config:
        env_file = ".env"
        env_prefix = "DB_"

    drivername: str = "postgresql+asyncpg"
    host: str
    username: str
    password: str
    port: int
    database: str

    # connection args

    @property
    def dsn(self):
        url = URL.create(
            drivername=self.drivername,
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            database=self.database,
        )
        return url.render_as_string(hide_password=False)


class Settings(BaseSettings):
    db: DatabaseSettings = DatabaseSettings()


settings = Settings()
