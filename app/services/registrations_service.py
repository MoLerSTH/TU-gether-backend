# app/services/registrations_service.py
from __future__ import annotations
from google.api_core.exceptions import FailedPrecondition
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import HTTPException
from google.cloud import firestore
from app.db.firebase import get_db
from app.services.status_service import compute_status, can_register, effective_capacity, now_utc
from app.schemas.event import StatusEnum

COLL_EVENTS = "events"
COLL_REG    = "registrations"

def _reg_id(event_id: str, user_id: str) -> str:
    return f"{event_id}_{user_id}"

def register(event_id: str, user_id: str, role: str = "user"):
    db: firestore.Client = get_db()
    ev_ref = db.collection(COLL_EVENTS).document(event_id)
    reg_id = _reg_id(event_id, user_id)
    main_reg_ref = db.collection(COLL_REG).document(reg_id)
    user_reg_ref  = db.collection("users").document(user_id).collection("registrations").document(event_id)
    event_reg_ref = ev_ref.collection("registrations").document(user_id)

    @firestore.transactional
    def _txn(txn: firestore.Transaction):
        ev_snap = ev_ref.get(transaction=txn)
        if not ev_snap.exists:
            raise ValueError("ไม่พบกิจกรรมนี้")
        ev = ev_snap.to_dict() or {}

        # sync status
        calc = compute_status(ev, now=now_utc())
        if (ev.get("status") or "") != calc.value:
            txn.update(ev_ref, {"status": calc.value, "updated_at": firestore.SERVER_TIMESTAMP})

        if calc == StatusEnum.UPCOMING:
            raise ValueError("ยังไม่ถึงเวลาเปิดลงทะเบียน")
        if calc == StatusEnum.CLOSE:
            raise ValueError("เลยกำหนดปิดรับสมัครแล้ว")
        if calc == StatusEnum.FULL:
            raise ValueError("กิจกรรมเต็มแล้ว")

        reg_snap = main_reg_ref.get(transaction=txn)
        if reg_snap.exists:
            return {"ok": True, "registration_id": reg_id, "duplicate": True}

        cap = effective_capacity(ev)
        current = int(ev.get("current_count", 0) or 0)
        if cap is not None and current >= cap:
            raise ValueError("กิจกรรมเต็มแล้ว (ครบจำนวน)")

        payload = {
            "event_id": event_id,
            "user_id": user_id,
            "role": role,
            "status": "confirmed",
            "registered_at": firestore.SERVER_TIMESTAMP,
            # denormalized
            "event_title": ev.get("title"),
            "event_faculty": ev.get("faculty"),
            "event_category": ev.get("category"),
            "event_tags": list(ev.get("tags", [])) if isinstance(ev.get("tags"), list) else [],
            "event_date": ev.get("event_date"),
            "deadline_date": ev.get("deadline_date"),
        }

        updates = {"current_count": current + 1}
        if cap is not None and (current + 1) >= cap:
            updates["status"] = StatusEnum.FULL.value
        txn.update(ev_ref, updates)

        txn.set(main_reg_ref, payload, merge=True)
        txn.set(user_reg_ref, payload, merge=True)
        txn.set(event_reg_ref, payload, merge=True)

        return {"ok": True, "registration_id": reg_id}

    txn = db.transaction()
    try:
        return _txn(txn)
    except ValueError as e:
        raise e
    except Exception as e:
        raise RuntimeError(f"ลงทะเบียนล้มเหลว: {e}")

def unregister(event_id: str, user_id: str):
    db: firestore.Client = get_db()
    ev_ref = db.collection(COLL_EVENTS).document(event_id)
    reg_id = _reg_id(event_id, user_id)
    main_reg_ref = db.collection(COLL_REG).document(reg_id)
    user_reg_ref = db.collection("users").document(user_id).collection("registrations").document(event_id)
    event_reg_ref = ev_ref.collection("registrations").document(user_id)

    @firestore.transactional
    def _txn(txn: firestore.Transaction):
        # 1) ต้องมีรายการลงทะเบียนก่อน
        reg_snap = main_reg_ref.get(transaction=txn)
        if not reg_snap.exists:
            raise ValueError("ยังไม่ได้ลงทะเบียนกิจกรรมนี้")

        # 2) อ่าน event ปัจจุบัน
        ev_snap = ev_ref.get(transaction=txn)
        current = 0
        if ev_snap.exists:
            ev = ev_snap.to_dict() or {}

            # policy: ไม่ให้ยกเลิกหลังเลย deadline ของ "event ปัจจุบัน"
            deadline = ev.get("deadline_date")
            if isinstance(deadline, datetime) and now_utc() > deadline:
                raise ValueError("เลยกำหนดปิดรับสมัครแล้ว ไม่สามารถยกเลิกได้")

            current = int(ev.get("current_count", 0) or 0)

        # 3) ปรับตัวนับและสถานะอีเวนท์
        new_count = max(0, current - 1)
        updates = {"current_count": new_count}

        if ev_snap.exists:
            ev_updated = {**(ev_snap.to_dict() or {}), **updates}
            new_status = compute_status(ev_updated, now=now_utc())
            updates["status"] = new_status.value

        txn.update(ev_ref, updates)

        # 4) ลบเอกสาร registration ทั้ง 3 จุด
        txn.delete(main_reg_ref)
        txn.delete(user_reg_ref)
        txn.delete(event_reg_ref)

        return {"ok": True, "unregistered": reg_id}

    txn = db.transaction()
    try:
        return _txn(txn)
    except ValueError as e:
        raise e
    except Exception as e:
        raise RuntimeError(f"ยกเลิกการลงทะเบียนล้มเหลว: {e}")

def status(event_id: str, user_id: str):
    db: firestore.Client = get_db()
    reg_id = _reg_id(event_id, user_id)
    snap = db.collection(COLL_REG).document(reg_id).get()
    if not snap.exists:
        return {"registered": False}
    data = snap.to_dict() or {}
    return {
        "registered": True,
        "status": data.get("status", "confirmed"),
        "registered_at": data.get("registered_at"),
        "event_faculty": data.get("event_faculty"),
        "event_category": data.get("event_category"),
        "event_tags": data.get("event_tags"),
        "event_date": data.get("event_date"),
        "deadline_date": data.get("deadline_date"),
    }

# --- ADD: serialize + list/get for history ---
def _serialize_registration(reg: Dict[str, Any], ev: Dict[str, Any] | None) -> Dict[str, Any]:
    ev = ev or {}
    try:
        ev_status = compute_status(ev, now=now_utc()).value
    except Exception:
        ev_status = (ev.get("status") or StatusEnum.UPCOMING.value)

    return {
        "registration_id": _reg_id(reg.get("event_id"), reg.get("user_id")),
        "event_id": reg.get("event_id"),
        "event_title": reg.get("event_title") or ev.get("title"),
        "event_date": reg.get("event_date") or ev.get("event_date"),
        "faculty": reg.get("event_faculty") or ev.get("faculty"),
        "category": reg.get("event_category") or ev.get("category"),
        "picture_url": ev.get("picture_url"),
        "tags": reg.get("event_tags") or ev.get("tags") or [],
        "role": reg.get("role") or "user",
        "event_status": ev_status,
        "user_status": reg.get("status", "confirmed"),
        "registered_at": reg.get("registered_at"),
        "attendance_at": reg.get("attendance_at"),
        "certificate_url": reg.get("certificate_url"),
        "deadline_date": reg.get("deadline_date") or ev.get("deadline_date"),
    }

def list_user_registrations(user_id: str, *, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    db: firestore.Client = get_db()
    col = db.collection(COLL_REG)
    try:
        q = (col.where("user_id", "==", user_id)
               .order_by("registered_at", direction=firestore.Query.DESCENDING))
        snaps = q.stream()
        used_fallback = False
    except FailedPrecondition:
        # ไม่มีดัชนี → fallback
        snaps = col.where("user_id", "==", user_id).stream()
        used_fallback = True

    out: List[Dict[str, Any]] = []
    for s in snaps:
        reg = s.to_dict() or {}
        ev_id = reg.get("event_id")
        ev_doc = db.collection(COLL_EVENTS).document(ev_id).get()
        ev = ev_doc.to_dict() if ev_doc.exists else {}
        item = _serialize_registration(reg, ev)
        if status_filter and item["user_status"] != status_filter:
            continue
        out.append(item)

    if used_fallback:
        # sort ในแอปเมื่อไม่มี index
        def _key(x):
            v = x.get("registered_at")
            return v if isinstance(v, datetime) else datetime.min
        out.sort(key=_key, reverse=True)
    return out
def get_registration(registration_id: str) -> Dict[str, Any]:
    db: firestore.Client = get_db()
    snap = db.collection(COLL_REG).document(registration_id).get()
    if not snap.exists:
        raise HTTPException(status_code=404, detail="ไม่พบรายการลงทะเบียน")
    reg = snap.to_dict() or {}
    ev_doc = db.collection(COLL_EVENTS).document(reg.get("event_id")).get()
    ev = ev_doc.to_dict() if ev_doc.exists else {}
    return _serialize_registration(reg, ev)
