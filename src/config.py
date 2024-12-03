import datetime
from logging import getLogger
from collections.abc import AsyncIterator, Generator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from jinja2_fragments.fastapi import Jinja2Blocks
from sqlmodel import Field, Session, SQLModel, create_engine, desc, select

DB_URL = "sqlite:///database_dailywork.db"
engine = create_engine(DB_URL)
templates = Jinja2Blocks(directory="templates")

_logger = getLogger(__name__)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


@asynccontextmanager
async def lifespan_event(app: FastAPI) -> AsyncIterator[None]:
    _logger.debug("Started lifespan event.")
    SQLModel.metadata.create_all(engine)
    assert app
    yield
    _logger.debug("Ending lifespan event.")


class Work(SQLModel, table=True):
    id: int | None = Field(primary_key=True, default=None)
    date: datetime.date
    tag: str
    done: str
    todo: str
    date_created: datetime.datetime = Field(default_factory=datetime.datetime.now)


class FormData(SQLModel):
    date: datetime.date
    tag: str
    todo: str
    done: str


class CRUD:
    @staticmethod
    async def create_new_work(s: Session, record: Work) -> None:
        s.add(record)
        s.commit()
        s.refresh(record)
        _logger.debug(f"{Work.__name__} created: {record}")

    @staticmethod
    async def delete_work(s: Session, id: int) -> None:
        current = s.get(Work, id)
        s.delete(current)
        s.commit()
        _logger.debug(f"{Work.__name__} with {id =} deleted.")

    @staticmethod
    async def get_all_works(
        s: Session, limit: int = 100, offset: int = 0
    ) -> list[Work]:
        query = (
            select(Work).order_by(desc(Work.date_created)).limit(limit).offset(offset)
        )
        recordlist = s.exec(query).all()
        _logger.debug(f"{Work.__name__} with {id =} deleted.")
        return recordlist
