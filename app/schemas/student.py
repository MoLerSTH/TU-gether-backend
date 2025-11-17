# app/schemas/student.py
from typing import Optional, Annotated
from pydantic import BaseModel, EmailStr, Field

class StudentIn(BaseModel):
    student_id: Annotated[str, Field(pattern=r"^\d{8,12}$")]
    citizen_id: Annotated[str, Field(pattern=r"^\d{13}$")]
    firstname: str
    lastname: str
    email: Optional[EmailStr] = None
    grade: Optional[int] = None
    phone: Optional[Annotated[str, Field(pattern=r"^\d{10}$")]] = None
    role: str = "student"

class StudentOut(BaseModel):
    student_id: str
    firstname: str
    lastname: str
    email: Optional[EmailStr] = None
    grade: Optional[int] = None
    phone: Optional[str] = None
    role: str = "student"
