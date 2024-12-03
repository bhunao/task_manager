from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session

from src.config import CRUD, FormData, Work, get_session, lifespan_event, templates

app = FastAPI(title="Daily Work", lifespan=lifespan_event)
app.mount("/static", StaticFiles(directory="static/"), name="static")

router = APIRouter()

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


@router.get("/about")
async def about_us(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})


app.include_router(router)
