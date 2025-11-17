# app/api/v1/routes_admin_users.py
from fastapi import APIRouter, HTTPException
from firebase_admin import firestore
from typing import List, Dict, Any
from passlib.hash import bcrypt

router = APIRouter(prefix="/api/users", tags=["users"])

# -------------------------------------------------
# 🔧 Helper: แปลง doc Firestore → JSON ที่ admin_user.js ใช้ได้
# -------------------------------------------------

def _serialize_general_user(doc) -> Dict[str, Any]:
    data = doc.to_dict() or {}

    full_name = (data.get("full_name") or "").strip()
    parts = full_name.split() if full_name else []

    first_from_full = parts[0] if len(parts) >= 1 else ""
    last_from_full  = " ".join(parts[1:]) if len(parts) >= 2 else ""

    firstname = data.get("firstname") or first_from_full
    lastname  = data.get("lastname") or last_from_full

    email = data.get("email") or ""
    phone = data.get("phone_num") or data.get("phone") or ""
    role  = (data.get("role") or "User").capitalize()

    return {
        "id": doc.id,
        "userType": "General",
        "username": data.get("username") or doc.id,
        "name": firstname,
        "lastname": lastname,
        "email": email,
        "phone": phone,
        "role": role,
    }


def _serialize_student(doc) -> Dict[str, Any]:
    data = doc.to_dict() or {}
    firstname = data.get("firstname") or ""
    lastname = data.get("lastname") or ""
    email = data.get("email") or ""
    faculty = data.get("faculty") or ""
    major = data.get("major") or ""
    grade = data.get("grade")  # ปี (int หรือ string)
    role = (data.get("role") or "student").capitalize()

    return {
        "id": doc.id,                         # ใช้ doc.id = studentId
        "userType": "Student",
        "studentId": doc.id,
        "name": firstname,
        "lastname": lastname,
        "email": email,
        # อย่าเปิดเผยเลขบัตรจริง ให้ placeholder ไปพอ (ฟอร์มฝั่งแก้ไขก็ lock ไว้อยู่แล้ว)
        "identificationId": "*************",
        "faculty": faculty,
        "major": major,
        "year": str(grade) if grade is not None else "",
        "role": role,
    }

# -------------------------------------------------
# 1) GET /api/users  → ดึง General + Student รวมกัน
# -------------------------------------------------

@router.get("/", response_model=List[Dict[str, Any]])
def list_users():
    db = firestore.client()

    users: List[Dict[str, Any]] = []

    # ----- General users จาก collection "users"
    users_ref = db.collection("users")
    for doc in users_ref.stream():
        users.append(_serialize_general_user(doc))

    # ----- Students จาก collection "Student"
    students_ref = db.collection("Student")
    for doc in students_ref.stream():
        users.append(_serialize_student(doc))

    return users


# -------------------------------------------------
# 2) POST /api/users  → สร้างผู้ใช้ใหม่ (General / Student)
#    ใช้ร่วมกับ admin_user.js (Add User)
# -------------------------------------------------

@router.post("/", response_model=Dict[str, Any])
def create_user(payload: Dict[str, Any]):
    db = firestore.client()

    user_type = payload.get("userType") or "General"

    # -----------------------------------------
    # ✅ สร้าง Student
    # -----------------------------------------
    if user_type == "Student":
        student_id = (payload.get("studentId") or "").strip()
        identification_id = (payload.get("identificationId") or "").strip()
        name = (payload.get("name") or "").strip()
        lastname = (payload.get("lastname") or "").strip()
        email = (payload.get("email") or "").strip()
        faculty = (payload.get("faculty") or "").strip()
        major = (payload.get("major") or "").strip()
        year = payload.get("year")

        if not student_id or not identification_id or not name or not lastname:
            raise HTTPException(400, "กรุณากรอก Student ID, เลขบัตรประชาชน, ชื่อ, นามสกุล")

        # ป้องกันซ้ำ
        stu_ref = db.collection("Student").document(student_id)
        if stu_ref.get().exists:
            raise HTTPException(400, "มี Student ID นี้ในระบบแล้ว")

        # hash เลขบัตร
        nid_hash = bcrypt.hash(identification_id)

        # grade เก็บเป็น int ถ้าแปลงได้
        grade = None
        try:
            if year not in (None, "", "all", "ทั้งหมด"):
                grade = int(year)
        except Exception:
            grade = None

        stu_ref.set({
            "firstname": name,
            "lastname": lastname,
            "email": email,
            "faculty": faculty,
            "major": major,
            "grade": grade,
            "phone_num": payload.get("phone") or "",
            "national_id_hash": nid_hash,
            "role": "student",
        })

        # ส่งกลับรูปแบบเดียวกับ list_users
        return _serialize_student(stu_ref.get())

    # -----------------------------------------
    # ✅ สร้าง General User (collection "users")
    # -----------------------------------------
    username = (payload.get("username") or "").strip()
    password = (payload.get("password") or "").strip()
    name = (payload.get("name") or "").strip()
    lastname = (payload.get("lastname") or "").strip()
    email = (payload.get("email") or "").strip()
    phone = (payload.get("phone") or "").strip()
    role = (payload.get("role") or "user").lower()

    if not username or not password:
        raise HTTPException(400, "กรุณากรอก Username และ Password")

    users_ref = db.collection("users").document(username)
    if users_ref.get().exists:
        raise HTTPException(400, "มี username นี้ในระบบแล้ว")

    pw_hash = bcrypt.hash(password)

    users_ref.set({
        "username": username,
        "user_id": payload.get("user_id") or username,  # ถ้าไม่มี user_id ก็ใช้ username ไปก่อน
        "password_hash": pw_hash,
        "firstname": name,
        "lastname": lastname,
        "full_name": f"{name} {lastname}".strip(),
        "email": email,
        "phone_num": phone,
        "role": role,
        # grade ถ้าอยากใช้ทีหลัง
        "grade": payload.get("grade"),
    })

    return _serialize_general_user(users_ref.get())


# -------------------------------------------------
# 3) PUT /api/users/{id}  → แก้ไขข้อมูล
#    id = doc.id (General = username, Student = studentId)
# -------------------------------------------------

@router.put("/{id}", response_model=Dict[str, Any])
def update_user(id: str, payload: Dict[str, Any]):
    db = firestore.client()
    user_type = payload.get("userType") or "General"

    # -----------------------------------------
    # ✅ แก้ Student
    # -----------------------------------------
    if user_type == "Student":
        stu_ref = db.collection("Student").document(id)
        doc = stu_ref.get()
        if not doc.exists:
            raise HTTPException(404, "ไม่พบ Student ที่จะแก้ไข")

        data = doc.to_dict() or {}
        # ID / เลขบัตรไม่ให้เปลี่ยน
        name = (payload.get("name") or data.get("firstname") or "").strip()
        lastname = (payload.get("lastname") or data.get("lastname") or "").strip()
        email = (payload.get("email") or data.get("email") or "").strip()
        faculty = (payload.get("faculty") or data.get("faculty") or "").strip()
        major = (payload.get("major") or data.get("major") or "").strip()
        year = payload.get("year", data.get("grade"))

        grade = data.get("grade")
        try:
            if year not in (None, "", "all", "ทั้งหมด"):
                grade = int(year)
        except Exception:
            pass

        updated = {
            **data,
            "firstname": name,
            "lastname": lastname,
            "email": email,
            "faculty": faculty,
            "major": major,
            "grade": grade,
        }
        stu_ref.update(updated)
        return _serialize_student(stu_ref.get())

    # -----------------------------------------
    # ✅ แก้ General user
    # -----------------------------------------
    user_ref = db.collection("users").document(id)
    doc = user_ref.get()
    if not doc.exists:
        raise HTTPException(404, "ไม่พบผู้ใช้ที่จะแก้ไข")

    data = doc.to_dict() or {}

    # **ไม่อนุญาตให้เปลี่ยน username ผ่าน API นี้**
    name = (payload.get("name") or data.get("firstname") or "").strip()
    lastname = (payload.get("lastname") or data.get("lastname") or "").strip()
    email = (payload.get("email") or data.get("email") or "").strip()
    phone = (payload.get("phone") or data.get("phone_num") or "").strip()
    role = (payload.get("role") or data.get("role") or "user").lower()
    new_password = (payload.get("password") or "").strip()

    update_data = {
        "firstname": name,
        "lastname": lastname,
        "full_name": f"{name} {lastname}".strip(),
        "email": email,
        "phone_num": phone,
        "role": role,
    }

    if new_password:
        update_data["password_hash"] = bcrypt.hash(new_password)

    user_ref.update(update_data)
    return _serialize_general_user(user_ref.get())


# -------------------------------------------------
# 4) DELETE /api/users/{id}
#    ลองลบจาก "users" ก่อน ถ้าไม่เจอค่อยไปลบใน "Student"
# -------------------------------------------------

@router.delete("/{id}")
def delete_user(id: str):
    db = firestore.client()

    # ลบจาก users ถ้ามี
    user_ref = db.collection("users").document(id)
    user_doc = user_ref.get()
    if user_doc.exists:
        user_ref.delete()
        return {"message": "Deleted user (general)"}

    # ไม่งั้นลองลบจาก Student
    stu_ref = db.collection("Student").document(id)
    stu_doc = stu_ref.get()
    if stu_doc.exists:
        stu_ref.delete()
        return {"message": "Deleted user (student)"}

    raise HTTPException(404, "ไม่พบผู้ใช้ที่จะลบ")
