from pydantic import BaseModel, Field
from typing import Literal

# เก็บเวลาเป็น ISO 8601 string (เช่น "2025-09-13T09:00:00Z")
ISOTime = str

class ModelBase(BaseModel):
    version: int = Field(default=1)

Visibility = Literal["public", "org", "private"]
