from datetime import date
from pydantic import BaseModel


class NotificationOut(BaseModel):
    id: str
    title: str
    message: str
    due_date: date | None = None
    remind_at: date | None = None
    entity_type: str
    entity_id: int
    field_id: int
    field_name: str
    days_before: int | None = None
