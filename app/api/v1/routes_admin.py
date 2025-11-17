# app/api/v1/routes_admin.py
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from google.api_core.exceptions import FailedPrecondition
from app.services.admin_guard import admin_guard
from app.schemas.event import EventIn, EventUpdate
from app.repositories import events_repo
from app.db.firebase import get_db

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/events")
def admin_list_events(
    faculty: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    cursor: Optional[str] = Query(None),
    _=Depends(admin_guard),
):
    try:
        return events_repo.list_events(
            faculty=faculty, category=category, status=status,
            from_date=from_date, to_date=to_date, tag=tag,
            limit=limit, cursor=cursor
        )
    except FailedPrecondition as e:
        raise HTTPException(400, f"Firestore index required: {e.message}")

@router.post("/events")
def admin_create_event(payload: EventIn, _=Depends(admin_guard)):
    try:
        return events_repo.create_event(payload)
    except Exception as e:
        raise HTTPException(400, f"Create failed: {e}")

@router.put("/events/{event_id}")
def admin_update_event(event_id: str, payload: EventUpdate, _=Depends(admin_guard)):
    try:
        return events_repo.update_event(event_id, payload)
    except KeyError:
        raise HTTPException(404, "Event not found")
    except Exception as e:
        raise HTTPException(400, f"Update failed: {e}")

@router.delete("/events/{event_id}")
def admin_delete_event(event_id: str, _=Depends(admin_guard)):
    try:
        events_repo.delete_event(event_id)
        return {"ok": True, "deleted": event_id}
    except KeyError:
        raise HTTPException(404, "Event not found")
    except Exception as e:
        raise HTTPException(400, f"Delete failed: {e}")

@router.get("/events/{event_id}/registrations")
def admin_list_event_registrations(event_id: str, _=Depends(admin_guard)):
    db = get_db()
    ev_ref = db.collection("events").document(event_id)
    if not ev_ref.get().exists:
        raise HTTPException(404, "Event not found")

    def _resolve_fullname(uid: str) -> str:
        stu = db.collection("Student").document(uid).get()
        if stu.exists:
            s = stu.to_dict() or {}
            fn = (s.get("firstname") or "").strip()
            ln = (s.get("lastname") or "").strip()
            full = (s.get("full_name") or f"{fn} {ln}").strip()
            if full:
                return full
        users = list(db.collection("users").where("user_id", "==", uid).limit(1).get())
        if users:
            u = users[0].to_dict() or {}
            full = (u.get("full_name")
                    or f"{(u.get('firstname') or '').strip()} {(u.get('lastname') or '').strip()}").strip()
            if full:
                return full
        return uid

    out = []
    for snap in ev_ref.collection("registrations").stream():
        d = snap.to_dict() or {}
        uid = d.get("user_id") or snap.id
        ra = d.get("registered_at")
        if hasattr(ra, "isoformat"):
            ra = ra.isoformat()
        out.append({
            "user_id": uid,
            "full_name": _resolve_fullname(uid),
            "role": d.get("role", ""),
            "registered_at": ra,
        })
    out.sort(key=lambda x: (x.get("registered_at") or ""), reverse=True)
    return out
