from typing import Callable
from functools import wraps
from sqlalchemy.exc import OperationalError
import logging

from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.core import database
from src.core.errors import HTTP500_DATABASE_ERROR


logger = logging.getLogger(__name__)


def handle_database_errors(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except OperationalError as ex:
            logger.error(f"database Operational Error {ex}")
            raise HTTP500_DATABASE_ERROR

    return wrapper


@handle_database_errors
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        database.create_db_and_tables()
    except OperationalError as ex:
        logger.error(f"database Operational Error error {ex}")

    assert app is not None
    yield
    logger.info("closing application lifespan.")
