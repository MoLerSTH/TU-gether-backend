# app/repositories/events_repo.py
from datetime import datetime, timezone
from typing import List, Optional
from google.cloud import firestore as gfs
from firebase_admin import firestore
from app.db.firebase import get_db
from app.schemas.event import EventIn, EventOut, EventUpdate, StatusEnum
from google.cloud.firestore_v1 import FieldFilter
from pydantic import ValidationError
from app.services.status_service import compute_status, now_utc       


COLLECTION = "events"

def _col(db: gfs.Client):
    return db.collection(COLLECTION)

def _serialize(doc: gfs.DocumentSnapshot) -> EventOut:
    data = doc.to_dict() or {}
    data["event_id"] = doc.id

    # Back-compat: location -> major
    if "major" not in data and "location" in data and data.get("location"):
        data["major"] = data["location"]

    # Defaults กันเอกสารเก่า
    data.setdefault("faculty", "")
    data.setdefault("tags", [])
    data["current_count"] = int(data.get("current_count") or 0)
    data["num_reg"] = int(data.get("num_reg") or data["current_count"])
    if "min_register" not in data and "min_registration" in data:
        data["min_register"] = data.get("min_registration")
    if "max_register" not in data and "max_registration" in data:
        data["max_register"] = data.get("max_registration")

    # ⬇️ คำนวณสถานะตามเวลา + sync คืน Firestore ถ้าเปลี่ยน
    try:
        calc = compute_status(data, now=now_utc())
        if (data.get("status") or "") != calc.value:
            try:
                doc.reference.update({"status": calc.value, "updated_at": firestore.SERVER_TIMESTAMP})
            except Exception:
                # ถ้า update ไม่ได้ ก็ข้ามเพื่อไม่ให้ลิสต์ล่ม
                pass
        data["status"] = calc.value  # ใช้ค่าที่คำนวณได้เสมอ
    except Exception:
        # ถ้าคำนวณผิดพลาด ให้ fallback เป็น UPCOMING
        data["status"] = StatusEnum.UPCOMING.value

    return EventOut(**data)

def _next_event_id(db: gfs.Client) -> str:
    last = _col(db).order_by("event_id", direction=firestore.Query.DESCENDING).limit(1).stream()
    last_id = "000000"
    for d in last:
        last_id = d.to_dict().get("event_id", "000000")
        break
    return str(int(last_id) + 1).zfill(6)

# ---------- CRUD ----------
def create_event(payload: EventIn) -> EventOut:
    db = get_db()
    eid = _next_event_id(db)
    now = datetime.now(timezone.utc)
    data = payload.model_dump(exclude_none=True)
    data.pop("status", None)

    data.update({
        "event_id": eid,
        "created_at": now,
        "updated_at": now,
        "current_count": 0,
        "num_reg": 0,
    })
    ref = _col(db).document(eid)
    ref.set(data)
    data = payload.model_dump(exclude_none=True) 
    return _serialize(ref.get())

def get_event(event_id: str) -> EventOut:
    db = get_db()
    snap = _col(db).document(event_id).get()
    if not snap.exists:
        raise KeyError("Event not found")
    return _serialize(snap)

def update_event(event_id: str, payload: EventUpdate) -> EventOut:
    db = get_db()
    ref = _col(db).document(event_id)
    if not ref.get().exists:
        raise KeyError("Event not found")
    updates = payload.model_dump(exclude_unset=True, exclude_none=True)  # partial + ไม่เขียน None
    updates.pop("status", None)
    updates["updated_at"] = datetime.now(timezone.utc)
    if updates:
        ref.update(updates)
    return _serialize(ref.get())

def delete_event(event_id: str) -> None:
    db = get_db()
    ref = _col(db).document(event_id)
    if not ref.get().exists:
        raise KeyError("Event not found")
    ref.delete()

def _aware_utc(dt: Optional[datetime]) -> Optional[datetime]:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt

def list_events(
    faculty: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    tag: Optional[str] = None,
    limit: int = 12,
    cursor: Optional[str] = None,
) -> List[EventOut]:
    db = get_db()
    q = _col(db)

    # Filters
    if faculty:
        q = q.where(filter=FieldFilter("faculty", "==", faculty))
    if category:
        q = q.where(filter=FieldFilter("category", "==", category))
    if status:
        q = q.where(filter=FieldFilter("status", "==", status))
    if tag:
        q = q.where(filter=FieldFilter("tags", "array_contains", tag))

    fd = _aware_utc(from_date)
    td = _aware_utc(to_date)
    if fd:
        q = q.where(filter=FieldFilter("event_date", ">=", fd))
    if td:
        q = q.where(filter=FieldFilter("event_date", "<=", td))

    # Ordering: ใช้คีย์เดียวเพื่อตัดปัญหา composite index (จะใช้ event_id หรือ event_date ตัวเดียวก็ได้)
    q = q.order_by("event_id", direction=firestore.Query.DESCENDING)

    # Cursor pagination: ใช้ DocumentSnapshot
    if cursor:
        cur_snap = _col(db).document(cursor).get()
        if cur_snap.exists:
            q = q.start_after(document=cur_snap)

    q = q.limit(limit)
    snaps = list(q.stream())

    out: List[EventOut] = []
    for s in snaps:
        try:
            out.append(_serialize(s))
        except ValidationError:
            continue
        except Exception:
            continue

    return out
