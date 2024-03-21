import os
from logging import config as logging_config

from pydantic import BaseSettings, PostgresDsn

from core.logger import LOGGING


logging_config.dictConfig(LOGGING)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, '.env')


class AppSettings(BaseSettings):
    app_title: str = 'Base Title'
    project_host: str = 'localhost'
    project_port: int = 8000
    database_dsn: PostgresDsn
    debug: bool = False

    class Config:
        env_file = ENV_PATH


settings = AppSettings()
