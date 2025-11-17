# app/schemas/event.py
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from enum import Enum

class StatusEnum(str, Enum):
    UPCOMING = "Upcoming"
    OPEN = "Open"
    CLOSE = "Close"
    FULL = "Full"

class EventBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    detail: str
    major: str
    faculty: str
    category: str
    event_date: datetime
    deadline_date: datetime
    register_open_at: Optional[datetime] = None  # ✅ เพิ่มฟิลด์เปิดลงทะเบียน
    picture_url: Optional[str] = None
    status: StatusEnum = StatusEnum.UPCOMING
    tags: List[str] = Field(default_factory=list)
    min_register: Optional[int] = Field(default=None, ge=0)
    max_register: Optional[int] = Field(default=None, ge=0)

class EventIn(EventBase):
    @field_validator("deadline_date")
    @classmethod
    def _deadline_not_after_event(cls, v: datetime, info):
        ev = info.data.get("event_date")
        if ev and v > ev:
            raise ValueError("deadline_date must be on/before event_date")
        return v

    @field_validator("register_open_at")
    @classmethod
    def _open_at_not_after_deadline(cls, v: Optional[datetime], info):
        if v is None:
            return v
        dl = info.data.get("deadline_date")
        if dl and v > dl:
            raise ValueError("register_open_at must be on/before deadline_date")
        return v

    @field_validator("max_register")
    @classmethod
    def _max_not_less_than_min(cls, v: Optional[int], info):
        mn = info.data.get("min_register")
        if v is not None and mn is not None and v < mn:
            raise ValueError("max_register must be >= min_register")
        return v

class EventUpdate(BaseModel):
    title: Optional[str] = None
    detail: Optional[str] = None
    major: Optional[str] = None
    faculty: Optional[str] = None
    category: Optional[str] = None
    event_date: Optional[datetime] = None
    deadline_date: Optional[datetime] = None
    register_open_at: Optional[datetime] = None
    picture_url: Optional[str] = None
    status: Optional[StatusEnum] = None  # จะถูกคำนวณทับโดย service
    tags: Optional[List[str]] = None
    min_register: Optional[int] = Field(default=None, ge=0)
    max_register: Optional[int] = Field(default=None, ge=0)

    @field_validator("max_register")
    @classmethod
    def _max_ge_min(cls, v: Optional[int], info):
        mn = info.data.get("min_register")
        if v is not None and mn is not None and v < mn:
            raise ValueError("max_register must be >= min_register")
        return v

class EventOut(EventBase):
    event_id: str
    created_at: datetime
    updated_at: datetime
    current_count: int = 0
    num_reg: int = 0
