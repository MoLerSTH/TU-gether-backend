# app/services/admin_guard.py
from fastapi import Depends, HTTPException, Request

from app.core.session import get_session

def admin_guard(request: Request):
    sess = get_session(request)
    if not sess or sess.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    return sess
