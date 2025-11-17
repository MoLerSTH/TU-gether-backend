# app/repositories/admin_repo.py
from typing import Optional, Dict, Any, Iterator
from app.db.firebase import get_db

COLL = "admins"

def find_admin_by_username(username: str) -> Optional[Dict[str, Any]]:
    if not username:
        return None
    db = get_db()
    snap = db.collection(COLL).document(username).get()
    if not snap.exists:
        return None
    data = snap.to_dict() or {}
    data["username"] = username
    return data

def create_admin(username: str, password_hash: str, display_name: str | None = None, status: str = "active"):
    db = get_db()
    ref = db.collection(COLL).document(username)
    if ref.get().exists:
        raise ValueError("admin username already exists")
    ref.set({
        "password_hash": password_hash,
        "display_name": display_name or username,
        "status": status,
        "role": "admin",
    })
    return {"ok": True, "username": username}

def update_admin_password_hash(username: str, new_bcrypt_hash: str):
    db = get_db()
    ref = db.collection(COLL).document(username)
    if not ref.get().exists:
        return
    ref.update({"password_hash": new_bcrypt_hash})

def list_admins() -> Iterator[Dict[str, Any]]:
    db = get_db()
    for d in db.collection(COLL).stream():
        data = d.to_dict() or {}
        data["username"] = d.id
        data.pop("password_hash", None)
        yield data
