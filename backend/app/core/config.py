from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "ITAM"
    env: str = "dev"
    database_url: str = "mysql+pymysql://itam:itam@localhost:3306/itam"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_hours: int = 24

    class Config:
        env_file = ".env"


settings = Settings()
