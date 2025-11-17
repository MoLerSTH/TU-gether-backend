# app/services/status_service.py
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from app.schemas.event import StatusEnum


def now_utc() -> datetime:
    """เวลาปัจจุบันแบบ timezone-aware (UTC)"""
    return datetime.now(timezone.utc)


def _dt(val: Any) -> Optional[datetime]:
    """
    คืนค่าเป็น datetime ถ้าเป็นชนิด datetime อยู่แล้ว
    (ไม่ parse string ที่นี่ เพราะฝั่ง repo/read จาก Firestore จะเป็น datetime อยู่แล้ว)
    """
    return val if isinstance(val, datetime) else None


def effective_capacity(ev: Dict[str, Any]) -> Optional[int]:
    """
    นิยามความจุ: ใช้ max_register ถ้าเป็น int >= 0, ไม่งั้น = None (ไม่จำกัด)
    """
    mx = ev.get("max_register", None)
    if isinstance(mx, int) and mx >= 0:
        return mx
    try:
        # เผื่อเคสเป็น float/string ตัวเลข
        mxn = int(mx)
        return mxn if mxn >= 0 else None
    except Exception:
        return None


def compute_status(ev: Dict[str, Any], now: Optional[datetime] = None) -> StatusEnum:
    """
    คำนวณสถานะตามเวลาและจำนวนผู้สมัคร:
      - ถ้ายังไม่ถึง register_open_at -> UPCOMING
      - ถ้าเลย deadline_date แล้ว -> CLOSE
      - ถ้ามี capacity และ current_count แตะเพดาน -> FULL
      - มิฉะนั้น -> OPEN
    หมายเหตุ: ถ้าไม่กำหนด register_open_at ถือว่าเปิดลงทะเบียนทันที
    """
    now = now or now_utc()

    open_at = _dt(ev.get("register_open_at"))   # อาจเป็น None = เปิดทันที
    deadline = _dt(ev.get("deadline_date"))
    current = int(ev.get("current_count", 0) or 0)
    cap = effective_capacity(ev)

    # 1) ก่อนเปิดลงทะเบียน
    if open_at and now < open_at:
        return StatusEnum.UPCOMING

    # 2) เลยกำหนดปิดรับสมัคร
    if deadline and now > deadline:
        return StatusEnum.CLOSE

    # 3) เต็มจำนวน
    if cap is not None and current >= cap:
        return StatusEnum.FULL

    # 4) เปิดรับสมัคร
    return StatusEnum.OPEN


def can_register(ev: Dict[str, Any], now: Optional[datetime] = None) -> bool:
    """พร้อมลงทะเบียนหรือไม่ (ตาม compute_status)"""
    st = compute_status(ev, now=now)
    return st == StatusEnum.OPEN
