from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from alembic import command
from alembic.config import Config

from app.core.config import settings
from app.core.projects.projects import projects
from app.core import api
from app.database import engine
from app.core.models import Base
from app.core.crud import (
    db_create_default_permissions_if_not_exists,
    db_create_default_super_admin_permissions_if_not_exists,
    db_create_default_group_admin_permissions_if_not_exists,
    db_create_default_project_admin_permissions_if_not_exists,
    db_create_default_project_user_permissions_if_not_exists,
    db_create_default_project_data_provider_permissions_if_not_exists,
    db_create_admin_user_if_not_exists,
    db_create_default_role_if_not_exists
)
import logging
from logging.config import dictConfig
from app.core.config import LogConfig
from app.database import get_db

dictConfig(LogConfig().model_dump())
logger = logging.getLogger("uvicorn.access")


def create_tables():
    Base.metadata.create_all(bind=engine)
    logger.info("create tables")
    # alembic_cfg = Config("/usr/src/app/alembic.ini")
    # command.upgrade(alembic_cfg, "head")


def create_default_user():
    check, msg = db_create_admin_user_if_not_exists(next(get_db()))

    if check:
        logger.info(msg)
    else:
        logger.error(msg)


def create_default_permissions():
    check, msg = db_create_default_permissions_if_not_exists(next(get_db()))

    if check:
        logger.info(msg)
    else:
        logger.error(msg)


def create_default_super_admin_roles():
    check, msg = db_create_default_super_admin_permissions_if_not_exists(next(get_db()))
    if check:
        logger.info(msg)
    else:
        logger.error(msg)


def create_default_group_admin_roles():
    check, msg = db_create_default_group_admin_permissions_if_not_exists(next(get_db()))
    if check:
        logger.info(msg)
    else:
        logger.error(msg)


def create_default_project_admin_roles():
    check, msg = db_create_default_project_admin_permissions_if_not_exists(next(get_db()))
    if check:
        logger.info(msg)
    else:
        logger.error(msg)


def create_default_project_user_roles():
    check, msg = db_create_default_project_user_permissions_if_not_exists(next(get_db()))
    if check:
        logger.info(msg)
    else:
        logger.error(msg)


def create_default_project_data_provider_roles():
    check, msg = db_create_default_project_data_provider_permissions_if_not_exists(next(get_db()))
    if check:
        logger.info(msg)
    else:
        logger.error(msg)


def create_default_roles():
    check, msg = db_create_default_role_if_not_exists(next(get_db()))
    if check:
        logger.info(msg)
    else:
        logger.error(msg)


def get_application():
    _app = FastAPI(title=settings.PROJECT_NAME, version=settings.TAG)
    _app.include_router(api.router)
    _app.include_router(projects,tags=['Projects'])

    _app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    create_tables()
    create_default_permissions()
    create_default_super_admin_roles()
    create_default_group_admin_roles()
    create_default_project_admin_roles()
    create_default_project_user_roles()
    create_default_project_data_provider_roles()
    create_default_user()
    create_default_roles()

    return _app


app = get_application()
