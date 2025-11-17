# app/core/security.py
import re, hmac, hashlib
from typing import Optional
import bcrypt
from fastapi import Header, HTTPException
from firebase_admin import auth

_BCRYPT_PREFIX = re.compile(r"^\$2[aby]\$\d{2}\$")

def hash_password_bcrypt(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def _is_sha256_hex(s: str) -> bool:
    return bool(s) and len(s) == 64 and all(c in "0123456789abcdef" for c in s.lower())

def verify_password(password: str, hashed: str) -> bool:
    """
    รองรับทั้ง bcrypt และ legacy sha256(hex) เพื่อช่วงเปลี่ยนผ่าน
    """
    if not hashed:
        return False
    if _BCRYPT_PREFIX.match(hashed):
        try:
            return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
        except Exception:
            return False
    if _is_sha256_hex(hashed):
        sha = hashlib.sha256(password.encode("utf-8")).hexdigest()
        return hmac.compare_digest(sha, hashed)
    return False

def needs_rehash(hashed: str) -> bool:
    """
    ถ้ายังเป็น sha256 (หรือไม่ใช่ bcrypt มาตรฐาน) ให้รีแฮชเป็น bcrypt เมื่อ login ผ่าน
    """
    return not _BCRYPT_PREFIX.match(hashed or "")

# (ถ้ายังใช้ตรวจ admin token)
async def require_admin(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(401, "Missing bearer token")
    token = authorization.split(" ",1)[1].strip()
    try:
        decoded = auth.verify_id_token(token)
    except Exception:
        raise HTTPException(401, "Invalid token")
    if not decoded.get("admin", False):
        raise HTTPException(403, "Admin only")
    return decoded
