from contextlib import asynccontextmanager
import datetime
from fastapi import APIRouter, Depends, FastAPI

from sqlmodel import Field, SQLModel, Session, create_engine


engine = create_engine("sqlite:///database_dailywork")


def get_session():
    with Session(engine) as session:
        SQLModel.metadata.create_all(engine)
        yield session


@asynccontextmanager
async def lifespan_event(app: FastAPI):
    assert app
    yield


app = FastAPI(title="Daily Work")

router = APIRouter()


class Work(SQLModel, table=True):
    id: int | None = Field(primary_key=True, default=None)
    date: (
        datetime.date
    )  # TODO: this field should auto transform from str to datetime.date
    done: str
    todo: str

    def convert_date_str_to_date(self):
        if isinstance(self.date, str):
            self.date = datetime.datetime.strptime(self.date, "%Y-%m-%d")


GetSession: Session = Depends(get_session)


@router.get("/health_check")
async def health_check():
    try:
        _session = get_session()
        db_session = "connected"
    except Exception as e:
        db_session = e

    return {"status": "ok", "database": db_session}


@router.post("/new")
async def save_new_work(record: Work, s: Session = GetSession):
    record.convert_date_str_to_date()

    s.add(record)
    s.commit()
    s.refresh(record)
    return record


app.include_router(router)
