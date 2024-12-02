import datetime
from collections.abc import Generator

from sqlmodel import Field, SQLModel, Session, create_engine, desc, select
from jinja2_fragments.fastapi import Jinja2Blocks


engine = create_engine("sqlite:///database_dailywork.db")
templates = Jinja2Blocks(directory="templates")


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        SQLModel.metadata.create_all(engine)
        yield session


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

    @staticmethod
    async def delete_work(s: Session, id: int) -> None:
        current = s.get(Work, id)
        s.delete(current)
        s.commit()

    @staticmethod
    async def get_all_works(s: Session) -> list[Work]:
        query = select(Work).order_by(desc(Work.date_created))
        recordlist = s.exec(query).all()
        return recordlist
