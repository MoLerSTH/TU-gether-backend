# app/api/v1/routes_student.py
from fastapi import APIRouter, Form
from typing import Optional
from app.schemas.student import StudentIn
from app.services.student_service import create_student_profile

router = APIRouter(prefix="/v1", tags=["students"])

@router.post("/student-form")
def upsert_student_form(
    student_id: str = Form(...),
    citizen_id: str = Form(...),
    firstname: str = Form(...),
    lastname: str = Form(...),
    email: Optional[str] = Form(None),
    grade: Optional[int] = Form(None),
    phone: Optional[str] = Form(None),
    role: Optional[str] = Form("student"),
):
    payload = StudentIn(
        student_id=student_id, citizen_id=citizen_id,
        firstname=firstname, lastname=lastname,
        email=email, grade=grade, phone=phone, role=role
    )
    return create_student_profile(payload)
