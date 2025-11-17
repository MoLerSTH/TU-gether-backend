# app/services/auth_service.py
import re
from fastapi import HTTPException
from app.core.security import (
    hash_password_bcrypt,
    verify_password,
    needs_rehash,
)
from app.repositories.user_repo import (
    user_exists, email_exists, phone_exists, add_user,
    find_user_by_username_or_email, get_next_user_id,
    update_user_password_hash,
)
from app.services.student_service import login_student

# 👇 เพิ่ม: ใช้ admin_repo เพื่อล็อกอินแอดมินผ่านช่องผู้ใช้ทั่วไป
from app.repositories.admin_repo import find_admin_by_username, update_admin_password_hash


def login_user(
    *,  # keyword-only
    user_type: str,
    identifier: str | None = None,
    password: str | None = None,
    student_id: str | None = None,
    citizen_id: str | None = None,
):
    """
    Handle login for:
      - user: (identifier=username หรือ @gmail.com) + password
        - ถ้าไม่พบใน users → จะลองเช็คใน admins ต่อ (ให้ล็อกอินผ่านช่องเดียวกันได้)
      - student: student_id + citizen_id
    รองรับทั้ง bcrypt และ legacy sha256; ถ้า login ผ่านและพบว่าเป็น sha256 จะ auto-upgrade -> bcrypt
    """
    if user_type == "user":
        if not identifier or not password:
            raise HTTPException(status_code=400, detail="กรุณากรอก อีเมล/ชื่อผู้ใช้ และรหัสผ่าน")

        # ถ้าเป็นอีเมล ให้บังคับ @gmail.com (สำหรับ users เท่านั้น)
        is_email = "@" in identifier
        if is_email:
            identifier = identifier.strip().lower()
            if not re.fullmatch(r"[A-Za-z0-9._%+-]+@gmail\.com", identifier):
                raise HTTPException(status_code=400, detail="อนุญาตเฉพาะอีเมล @gmail.com")

        # ---- ลองผู้ใช้ทั่วไปก่อน
        ref, data = find_user_by_username_or_email(identifier)
        if data:
            saved = data.get("password_hash") or ""
            if not verify_password(password, saved):
                raise HTTPException(status_code=401, detail="รหัสผ่านไม่ถูกต้อง")

            # อัปเกรด hash เป็น bcrypt ถ้ายังไม่ใช่
            if needs_rehash(saved):
                try:
                    new_hash = hash_password_bcrypt(password)
                    update_user_password_hash(data["username"], new_hash)
                except Exception:
                    pass

            return {
                "message": f"ยินดีต้อนรับ {data.get('username')}",
                "user_id": data.get("user_id"),
                "role": data.get("role", "other"),
                "full_name": data.get("full_name") or f"{data.get('firstname','')} {data.get('lastname','')}".strip() or data.get("username"),
                "username": data.get("username"),
            }

        # ---- ถ้าไม่พบ user → ลองแอดมินต่อ (ล็อกอินผ่านช่องเดียวกันได้)
        # หมายเหตุ: แอดมินจะใช้ username (doc id) ไม่บังคับ @gmail.com
        admin = find_admin_by_username(identifier)
        if not admin:
            raise HTTPException(status_code=404, detail="ไม่พบบัญชีผู้ใช้")

        saved = admin.get("password_hash") or ""
        if not verify_password(password, saved):
            raise HTTPException(status_code=401, detail="รหัสผ่านไม่ถูกต้อง")

        # อัปเกรด hash ถ้าจำเป็น
        if needs_rehash(saved):
            try:
                new_hash = hash_password_bcrypt(password)
                update_admin_password_hash(admin["username"], new_hash)
            except Exception:
                pass

        # ตรวจสถานะ
        if admin.get("status", "active") != "active":
            raise HTTPException(status_code=403, detail="บัญชีผู้ดูแลถูกระงับการใช้งาน")

        # คืนค่า role=admin
        return {
            "message": f"ยินดีต้อนรับผู้ดูแล {admin.get('display_name') or admin.get('username')}",
            "user_id": admin.get("username"),
            "role": "admin",
            "full_name": admin.get("display_name") or admin.get("username"),
            "username": admin.get("username"),
        }

    elif user_type == "student":
        if not student_id or not citizen_id:
            raise HTTPException(status_code=400, detail="กรุณากรอก รหัสนักศึกษา และ เลขบัตรประชาชน")
        return login_student(student_id, citizen_id)

    else:
        raise HTTPException(status_code=400, detail="ประเภทผู้ใช้ไม่ถูกต้อง")


def register_user(
    username: str,
    password: str,
    confirm_password: str,
    email: str,
    grade: str,
    phone_num: str,
    role: str,
    firstname: str,
    lastname: str,
):
    email = (email or "").strip().lower()
    phone_num = (phone_num or "").strip()

    if password != confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    if not re.fullmatch(r"\S{8,12}", password):
        raise HTTPException(status_code=400, detail="Password must be 8–12 non-space characters")
    if not re.fullmatch(r"[A-Za-z0-9._%+-]+@gmail\.com", email):
        raise HTTPException(status_code=400, detail="Email must be a @gmail.com address")
    if not re.fullmatch(r"\d{10}", phone_num):
        raise HTTPException(status_code=400, detail="Phone number must be 10 digits")
    if str(grade) not in {"1", "2", "3", "4", "5", "6"}:
        raise HTTPException(status_code=400, detail="Invalid grade (allowed: 1,2,3,4,5,6)")

    if user_exists(username):
        raise HTTPException(status_code=400, detail="Username already exists")
    if email_exists(email):
        raise HTTPException(status_code=400, detail="Email already registered")
    if phone_exists(phone_num):
        raise HTTPException(status_code=400, detail="Phone number already registered")

    seq_user_id = get_next_user_id()
    full_name = f"{firstname.strip()} {lastname.strip()}".strip()
    user_data = {
        "user_id": seq_user_id,
        "username": username,
        "password_hash": hash_password_bcrypt(password),
        "email": email,
        "firstname": firstname.strip(),
        "lastname": lastname.strip(),
        "full_name": full_name,
        "grade": int(grade),
        "phone_num": phone_num,
        "role": role or "other",
    }
    add_user(user_data)
    return {"message": "User registered successfully!", "username": username}
