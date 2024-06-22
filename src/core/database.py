from typing import TypeVar
import logging

from typing import Generator

from sqlmodel import SQLModel as MODEL
from sqlmodel import select
from databases import DatabaseURL
from starlette.datastructures import Secret

from sqlmodel import create_engine
from sqlmodel import Session

from src.core.config import config


logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s | %(levelname)s | %(name)s.%(funcName)s]: %(message)s"
)

POSTGRES_USER = config("POSTGRES_USER", default="USER", cast=str)
POSTGRES_PASSWORD = config(
    "POSTGRES_PASSWORD", default="PASSWORD", cast=Secret)
POSTGRES_SERVER = config("POSTGRES_SERVER", cast=str, default="db")
POSTGRES_PORT = config("POSTGRES_PORT", cast=str, default="5432")
POSTGRES_DB = config("POSTGRES_DB", cast=str, default="default_db")
DATABASE_URL = config(
    "DATABASE_URL",
    cast=DatabaseURL,
    default=f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}",
)

postgre_url = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
engine = create_engine(postgre_url, echo=False)


def create_db_and_tables():
    MODEL.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


MODEL_T = TypeVar("MODEL_T", bound=MODEL)


class BaseDatabase:
    def __init__(self, session: Session):
        self.session: Session = session

    def create(self, record: MODEL, table: MODEL = None) -> MODEL:
        table = table if table else record.__class__

        new_record = table.model_validate(record, from_attributes=True)
        self.session.add(new_record)
        self.session.commit()
        self.session.refresh(new_record)
        return new_record

    def read(self, table: MODEL_T, id: int) -> MODEL_T | None:
        db_record = self.session.get(table, id)
        return db_record

    def read_all(
            self,
            table: MODEL = None,
            skip: int = 0,
            limit: int = 100
    ) -> list[MODEL]:
        query = select(table).offset(skip).limit(limit)
        result = self.session.exec(query).all()
        return result

    def update(self, record: MODEL, table: MODEL = None) -> MODEL | None:
        table = table if table else record.__class__
        db_record = self.session.get(table, record.id)
        if db_record is None:
            return None
        db_record.sqlmodel_update(record)
        self.session.add(db_record)
        self.session.commit()
        self.session.refresh(db_record)
        return db_record

    def delete(self, table: MODEL, id: int) -> MODEL | None:
        db_record = self.session.get(table, id)
        if db_record is None:
            return None
        self.session.delete(db_record)
        self.session.commit()
        return db_record
