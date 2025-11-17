# app/repositories/registrations_repo.py
from datetime import datetime
from app.db.firebase import get_db

COLL = "registrations"

def register_user_to_event(user_id: str, event_id: str, role: str):
    db = get_db()
    reg_id = f"{event_id}_{user_id}"
    ref = db.collection(COLL).document(reg_id)
    if ref.get().exists:
        raise ValueError("Already registered")
    ref.set({
        "event_id": event_id,
        "user_id": user_id,
        "role": role,
        "created_at": datetime.utcnow(),
    })
    return {"message": "Registered successfully", "event_id": event_id}

def unregister_user_from_event(user_id: str, event_id: str):
    db = get_db()
    reg_id = f"{event_id}_{user_id}"
    ref = db.collection(COLL).document(reg_id)
    if not ref.get().exists:
        raise ValueError("Not registered")
    ref.delete()
    return {"message": "Unregistered successfully", "event_id": event_id}

def check_registration(user_id: str, event_id: str) -> bool:
    db = get_db()
    reg_id = f"{event_id}_{user_id}"
    return db.collection(COLL).document(reg_id).get().exists

