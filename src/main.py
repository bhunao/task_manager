from contextlib import asynccontextmanager
import datetime
from typing import Annotated
from fastapi import APIRouter, Depends, FastAPI, Form, Request

from fastapi.responses import HTMLResponse
from sqlmodel import Field, SQLModel, Session, create_engine, desc, select
from jinja2_fragments.fastapi import Jinja2Blocks


engine = create_engine("sqlite:///database_dailywork.db")

templates = Jinja2Blocks(directory="templates")


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


SeessionDep: Session = Depends(get_session)


@router.get("/", response_class=HTMLResponse)
async def read_index(request: Request, s: Session = SeessionDep):
    recordlist = await CRUD.get_all_works(s)
    return templates.TemplateResponse(
        "index.html", {"request": request, "recordlist": recordlist}
    )


@router.post("/work", response_class=HTMLResponse)
async def create_work(
    request: Request, form_data: Annotated[FormData, Form()], s: Session = SeessionDep
):
    assert request
    record = Work.model_validate(form_data)
    await CRUD.create_new_work(s, record)
    return templates.TemplateResponse(
        "work_card.html", {"request": request, "record": record}
    )


@router.delete("/work/{id}", response_class=HTMLResponse)
async def delete_work(id: int, s: Session = SeessionDep):
    await CRUD.delete_work(s, id)
    return HTMLResponse()


@router.get("/health_check")
async def health_check():
    try:
        _session = get_session()
        db_session = "connected"
    except Exception as e:
        db_session = e

    return {"status": "ok", "database": db_session}


app.include_router(router)
