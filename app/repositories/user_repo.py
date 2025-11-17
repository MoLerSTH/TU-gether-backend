# app/repositories/user_repo.py
from __future__ import annotations

from typing import Iterator, Tuple, Optional, Dict, Any
from google.cloud import firestore as gcf
from app.db.firebase import get_db

COLL_USERS = "users"

def user_exists(username: str) -> bool:
    db = get_db()
    return db.collection(COLL_USERS).document(username).get().exists

def email_exists(email: str) -> bool:
    email = (email or "").strip().lower()
    db = get_db()
    q = list(db.collection(COLL_USERS).where("email", "==", email).limit(1).get())
    return len(q) > 0

def phone_exists(phone_num: str) -> bool:
    phone_num = (phone_num or "").strip()
    db = get_db()
    q = list(db.collection(COLL_USERS).where("phone_num", "==", phone_num).limit(1).get())
    return len(q) > 0

def add_user(user_data: Dict[str, Any]) -> None:
    # สมมุติว่า service เตรียมข้อมูลถูกต้องแล้ว (username เป็น doc id, password_hash เป็น bcrypt)
    db = get_db()
    db.collection(COLL_USERS).document(user_data["username"]).set(user_data)

def find_user_by_username_or_email(identifier: str) -> Tuple[Optional[Any], Optional[Dict[str, Any]]]:
    """
    คืน (ref, data) ถ้าเจอ ไม่งั้น (None, None)
    - ถ้า identifier เป็น username จะหา doc id ตรง ๆ ก่อน
    - ถ้าไม่เจอค่อยหา email ที่เท่ากัน (lower)
    """
    db = get_db()
    ident = (identifier or "").strip()
    # 1) ลอง username ตรง ๆ ก่อน (doc id)
    doc = db.collection(COLL_USERS).document(ident).get()
    if doc.exists:
        ref = db.collection(COLL_USERS).document(ident)
        return ref, (doc.to_dict() or {})

    # 2) หาอีเมล
    email = ident.lower()
    q = list(db.collection(COLL_USERS).where("email", "==", email).limit(1).get())
    if q:
        ref = db.collection(COLL_USERS).document(q[0].id)
        return ref, (q[0].to_dict() or {})
    return None, None

# --- running id with transaction ---
@gcf.transactional
def _txn_reserve_user_id(transaction, counters_ref) -> str:
    snap = counters_ref.get(transaction=transaction)
    if snap.exists and "next_user_seq" in (snap.to_dict() or {}):
        next_val = int(snap.to_dict()["next_user_seq"])
    else:
        next_val = 1
    transaction.set(counters_ref, {"next_user_seq": next_val + 1}, merge=True)
    return f"{next_val:05d}"

def get_next_user_id() -> str:
    db = get_db()
    counters_ref = db.collection("meta").document("counters")
    txn = db.transaction()
    return _txn_reserve_user_id(txn, counters_ref)

def list_users() -> Iterator[Dict[str, Any]]:
    db = get_db()
    # user_id เป็น string zero-pad (เช่น 00001) จึง order_by ตรง ๆ ได้
    docs = db.collection(COLL_USERS).order_by("user_id").stream()
    for d in docs:
        u = d.to_dict() or {}
        u.pop("password_hash", None)
        yield u

def update_user_password_hash(username: str, new_bcrypt_hash: str) -> None:
    db = get_db()
    ref = db.collection(COLL_USERS).document(username)
    snap = ref.get()
    if not snap.exists:
        return
    ref.update({
        "password_hash": new_bcrypt_hash,
        # เพิ่ม updated_at ไว้ตรวจสอบภายหลัง (ออปชัน—ลบได้ถ้าไม่ต้องใช้)
        # "updated_at": gcf.SERVER_TIMESTAMP,
    })
