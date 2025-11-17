# app/schemas/registration.py
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class RegistrationOut(BaseModel):
    registration_id: str
    event_id: str
    event_title: Optional[str] = None
    event_date: Optional[datetime] = None
    faculty: Optional[str] = None
    category: Optional[str] = None
    picture_url: Optional[str] = None
    tags: List[str] = []
    role: str = "user"
    event_status: Optional[str] = None   # computed
    user_status: str = "confirmed"
    registered_at: Optional[datetime] = None
    attendance_at: Optional[datetime] = None
    certificate_url: Optional[str] = None
    deadline_date: Optional[datetime] = None
