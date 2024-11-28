from contextlib import asynccontextmanager
import datetime
from typing import Annotated
from fastapi import APIRouter, Depends, FastAPI, Form, Request

from fastapi.responses import HTMLResponse
from sqlmodel import Field, SQLModel, Session, create_engine
from jinja2_fragments.fastapi import Jinja2Blocks


engine = create_engine("sqlite:///database_dailywork")

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
    date: (
        datetime.date
    )  # TODO: this field should auto transform from str to datetime.date
    done: str
    todo: str

    def convert_date_str_to_date(self):
        if isinstance(self.date, str):
            self.date = datetime.datetime.strptime(self.date, "%Y-%m-%d")


GetSession: Session = Depends(get_session)


class FormData(SQLModel):
    date: datetime.date
    code: str
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
async def read_index(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})


@router.get("/new_test", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("create_work_form.html", {"request": request})


@router.post("/test_form", response_class=HTMLResponse)
async def test_form(request: Request, form_data: Annotated[FormData, Form()]):
    assert request
    return f"{'<br>'.join(f'{k}:{v}' for k, v in form_data.model_dump().items())} <hr>"


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
