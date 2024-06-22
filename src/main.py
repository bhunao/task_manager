import logging

from datetime import datetime

from typing import Optional

from fastapi import FastAPI, Depends, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session

from src.core.config import templates
from src.core.database import get_session
from src.core.dependencies import lifespan
from src.database import Database
from src.models import Task


app = FastAPI(
    title="Task Manager",
    version="0.0.1",
    lifespan=lifespan
)
logger = logging.getLogger(__name__)


def days_diff(value: datetime):
    today = datetime.today()
    diff = today - value
    seconds = diff.total_seconds()
    if diff.days > 0:
        return f"{diff.days} days ago"
    elif seconds > 120:
        minutes = int(seconds // 60)
        return f"{minutes} minutes ago"
    else:
        return "a few seconds ago"


def yyyy_mm_dd(value: datetime):
    return value.strftime('%Y-%m-%d')


def hh_mm(value: datetime):
    return value.strftime('%H:%M')


# Register the custom filter
templates.env.filters['days_diff'] = days_diff
templates.env.filters['yyyy_mm_dd'] = yyyy_mm_dd
templates.env.filters['hh_mm'] = hh_mm

app.mount("/static", StaticFiles(directory="src/static/"), name="static")


@app.post("/new", response_class=HTMLResponse)
async def new_task(
    request: Request,
    name: str = Form(...),
    done: str = Form(...),
    todo: Optional[str] = Form(...),
    session: Session = Depends(get_session)
) -> str:
    db = Database(session)
    new_task = Task(
        name=name,
        done=done,
        todo=todo,
    )
    task = db.create(new_task)
    print("novo : ", task)
    return templates.TemplateResponse(
        "task_card.html",
        {"request": request, "task": task},
        block_name="task_card",
    )


@ app.get("/", response_class=HTMLResponse)
async def home(
    request: Request,
    session: Session = Depends(get_session)
) -> str:
    db = Database(session)
    task_list = db.read_all(Task)[::-1]
    return templates.TemplateResponse(
        "task_card.html",
        {"request": request, "task_list": task_list},
        block_name=None,
    )
