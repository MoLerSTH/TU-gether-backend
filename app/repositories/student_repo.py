# app/repositories/student_repo.py
import re
import hashlib
from fastapi import HTTPException
from google.cloud import firestore as gcf
from firebase_admin import firestore  # ✅ ใช้ DELETE_FIELD
from app.db.firebase import get_db
from app.core.security import hash_password_bcrypt  # ✅ เก็บ bcrypt เท่านั้น

COLL_STUDENTS = "Student"

def find_student_by_student_id(student_id: str):
    db = get_db()
    doc_ref = db.collection(COLL_STUDENTS).document(student_id)
    snap = doc_ref.get()
    if not snap.exists:
        return None, None
    return doc_ref, (snap.to_dict() or {})

@gcf.transactional
def _txn_create_student(transaction, stu_ref, uniq_sid_ref, uniq_nid_ref, uniq_email_ref, doc, sid):
    if stu_ref.get(transaction=transaction).exists:
        raise HTTPException(status_code=400, detail="student_id already exists")
    if uniq_sid_ref.get(transaction=transaction).exists:
        raise HTTPException(status_code=400, detail="student_id already exists")
    if uniq_nid_ref.get(transaction=transaction).exists:
        raise HTTPException(status_code=400, detail="national id already exists")
    if uniq_email_ref and uniq_email_ref.get(transaction=transaction).exists:
        raise HTTPException(status_code=400, detail="email already exists")

    transaction.create(uniq_sid_ref, {"student_id": sid})
    transaction.create(uniq_nid_ref, {"student_id": sid})
    if uniq_email_ref:
        transaction.create(uniq_email_ref, {"student_id": sid})
    transaction.create(stu_ref, doc)

def create_student(payload) -> dict:
    db = get_db()
    sid = payload.student_id.strip()
    cid = payload.citizen_id.strip()
    email = (payload.email or "").strip().lower()
    phone = (payload.phone or "").strip()

    if not re.fullmatch(r"\d{8,12}", sid):
        raise HTTPException(status_code=400, detail="student_id ต้องเป็นตัวเลข 8–12 หลัก")
    if not re.fullmatch(r"\d{13}", cid):
        raise HTTPException(status_code=400, detail="citizen_id ต้องเป็นตัวเลข 13 หลัก")
    if email and not re.fullmatch(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", email):
        raise HTTPException(status_code=400, detail="รูปแบบอีเมลไม่ถูกต้อง")
    if phone and not re.fullmatch(r"^\d{10}$", phone):
        raise HTTPException(status_code=400, detail="เบอร์โทรต้องเป็นตัวเลข 10 หลัก")
    if payload.grade is not None and payload.grade not in {1,2,3,4,5,6}:
        raise HTTPException(status_code=400, detail="grade ต้องเป็น 1–6")

    # ✅ เก็บ bcrypt สำหรับฟิลด์หลัก
    nid_bcrypt = hash_password_bcrypt(cid)
    # ✅ ใช้ sha256 hex สำหรับ unique-index doc id (ห้ามใช้ bcrypt เพราะมี '/')
    nid_sha = hashlib.sha256(cid.encode("utf-8")).hexdigest()

    stu_ref = db.collection(COLL_STUDENTS).document(sid)
    uniq_sid_ref   = db.collection("unique_students_sid").document(sid)
    uniq_nid_ref   = db.collection("unique_students_nid").document(nid_sha)  # ✅ safe doc id
    uniq_email_ref = db.collection("unique_students_email").document(email) if email else None

    doc = {
        "firstname": payload.firstname.strip(),
        "lastname":  payload.lastname.strip(),
        "email":     email or None,
        "grade":     payload.grade,
        "phone":     phone or None,
        "role":      (payload.role or "student"),
        "national_id_hash": nid_bcrypt,  # ✅ bcrypt stored
    }
    doc = {k: v for k, v in doc.items() if v is not None}

    try:
        txn = db.transaction()
        _txn_create_student(txn, stu_ref, uniq_sid_ref, uniq_nid_ref, uniq_email_ref, doc, sid)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create student: {e}")

    return {
        "message": "Student created successfully",
        "student_id": sid,
        "stored_fields": sorted(doc.keys()),
    }

def update_student_nid_hash(student_id: str, new_bcrypt_hash: str):
    db = get_db()
    doc_ref = db.collection(COLL_STUDENTS).document(student_id)
    if not doc_ref.get().exists:
        raise HTTPException(status_code=404, detail="student not found")
    # ✅ อัปเดตเป็น bcrypt และลบฟิลด์ legacy
    doc_ref.update({
        "national_id_hash": new_bcrypt_hash,
        "citizen_id": firestore.DELETE_FIELD,
        "national_id": firestore.DELETE_FIELD,
        "citizen_id_hash": firestore.DELETE_FIELD,
        "cid_hash": firestore.DELETE_FIELD,
    })
