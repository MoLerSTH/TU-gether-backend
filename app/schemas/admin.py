# app/schemas/admin.py
from pydantic import BaseModel, Field
from typing import Literal, Optional

AdminStatus = Literal["active", "disabled"]

class AdminIn(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=72)  # bcrypt safe
    display_name: Optional[str] = None
    status: AdminStatus = "active"

class AdminOut(BaseModel):
    username: str
    display_name: Optional[str] = None
    status: AdminStatus = "active"
    role: str = "admin"
