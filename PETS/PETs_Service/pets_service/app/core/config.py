import os
from pathlib import Path
from typing import Any, List, Optional, Union

from pydantic import BaseModel, ConfigDict, AnyHttpUrl, MariaDBDsn, field_validator
from pydantic_settings import BaseSettings
from pydantic_core.core_schema import FieldValidationInfo


class Settings(BaseSettings):
    PROJECT_NAME: str
    TAG: str
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode='before')
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    DB_SERVER: str
    DB_USER: str
    DB_PASSWORD: str
    DB_PRODDB: str
    DB_PORT: int
    DATABASE_URI: Optional[str] = None

    @field_validator("DATABASE_URI", mode='before')
    def assemble_db_connection(cls, v: Optional[str], info: FieldValidationInfo) -> Any:
        if isinstance(v, str):
            return v
        return MariaDBDsn.build(
            scheme="mariadb+pymysql",
            username=info.data.get("DB_USER"),
            password=info.data.get("DB_PASSWORD"),
            host=info.data.get("DB_SERVER"),
            path=info.data.get('DB_PRODDB'),
            port=int(info.data.get('DB_PORT')),
        ).unicode_string()

    LOG_FILE: str = "/usr/src/app/log/api.log"

    @field_validator("LOG_FILE", mode='before')
    def check_log_folder(cls, v: str) -> str:
        LOG_FILE = Path(v)
        LOG_PATH = LOG_FILE.parent
        if not LOG_PATH.exists():
            LOG_PATH.mkdir(parents=True, exist_ok=True)
        return v

    # system default user
    DEFAULT_USER: str
    DEFAULT_PASSWORD: str
    ACCOUNT_LOCKOUT_DURATION: int

    # JWT config
    JWT_ALGORITHM: str
    JWT_SECRET_KEY: str

    class Config:
        extra = 'allow'
        env_file_encoding = 'utf-8'

        @classmethod
        def customise_sources(
                cls,
                init_settings,
                env_settings,
                file_secret_settings,
        ):
            return file_secret_settings, env_settings, init_settings

        case_sensitive = True
        secrets_dir = "/var/run/secrets"
        env_file = ".env"


settings = Settings()


class IgnoredType:
    pass


class LogConfig(BaseModel):
    """Logging configuration to be set for the server"""

    model_config = ConfigDict(arbitrary_types_allowed=True, ignored_types=(IgnoredType,))

    LOGGER_NAME: str = "petsservice"
    LOG_FORMAT: str = f"%(asctime)s | {LOGGER_NAME} | %(levelprefix)s %(message)s (%(filename)s:%(lineno)d)"
    LOG_LEVEL: str = os.environ.get('LOGLEVEL', 'INFO').upper()
    LOG_FILE: str = "/usr/src/app/log/api.log"

    # Logging config
    version: int = 1
    disable_existing_loggers: bool = False
    formatters: IgnoredType = {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "use_colors": True,
        },
    }
    handlers: IgnoredType = {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "logfilerotating": {
            "formatter": "default",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": LOG_FILE,
            "when": "D",
            "interval": 2,
            "backupCount": 7,
        },
    }
    loggers: IgnoredType = {
        "uvicorn": {"handlers": ["default", "logfilerotating"], "level": LOG_LEVEL},
    }

