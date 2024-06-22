from datetime import datetime
from typing import Optional

from sqlmodel import Field

from src.core.database import MODEL


class Task(MODEL, table=True):
    id: int = Field(default=None, primary_key=True)
    date_created: datetime = Field(default_factory=datetime.now)
    last_update: datetime = Field(default_factory=datetime.now)
    name: str
    link: Optional[str] = None
    type: Optional[str] = None
    done: Optional[str] = None
    todo: Optional[str] = None
