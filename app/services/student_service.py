# app/services/student_service.py
import re
from fastapi import HTTPException
from app.core.security import verify_password, hash_password_bcrypt, needs_rehash
from app.repositories.student_repo import (
    find_student_by_student_id, create_student, update_student_nid_hash
)

def login_student(student_id: str, citizen_id: str):
    if not student_id or not citizen_id:
        raise HTTPException(status_code=400, detail="กรอก รหัสนักศึกษา และ เลขบัตรประชาชน")
    student_id = student_id.strip()
    citizen_id = citizen_id.strip()

    if not re.fullmatch(r"\d{8,12}", student_id):
        raise HTTPException(status_code=400, detail="รูปแบบรหัสนักศึกษาไม่ถูกต้อง")
    if not re.fullmatch(r"\d{13}", citizen_id):
        raise HTTPException(status_code=400, detail="เลขบัตรประชาชนต้อง 13 หลัก")

    ref, data = find_student_by_student_id(student_id)
    if not data:
        raise HTTPException(status_code=404, detail="ไม่พบนักศึกษานี้ในระบบ")

    saved = (
        data.get("national_id_hash") or
        data.get("citizen_id_hash")  or
        data.get("cid_hash")         or
        data.get("citizen_id")       or
        data.get("national_id")
    )

    if not saved or not verify_password(citizen_id, saved):
        raise HTTPException(status_code=401, detail="เลขบัตรประชาชนไม่ถูกต้อง")

    if needs_rehash(saved):
        try:
            update_student_nid_hash(student_id, hash_password_bcrypt(citizen_id))
        except Exception:
            pass

    full_name = f"{data.get('firstname','')} {data.get('lastname','')}".strip()
    display_name = data.get("username") or full_name or student_id

    return {
        "message": f"ยินดีต้อนรับ {display_name}",
        "user_id": student_id,
        "role": "student",
        "full_name": full_name or display_name,
        "username": data.get("username") or student_id,
    }

def create_student_profile(payload):
    return create_student(payload)
