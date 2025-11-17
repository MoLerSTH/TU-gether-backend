import json, time, hmac, hashlib, base64
from fastapi import Request, Response, HTTPException
from app.core.config import settings

SECRET = getattr(settings, "SESSION_SECRET", "CHANGE_ME_SESSION_SECRET")
COOKIE_NAME = getattr(settings, "COOKIE_NAME", "session")
COOKIE_SECURE = getattr(settings, "COOKIE_SECURE", False)
COOKIE_SAMESITE = getattr(settings, "COOKIE_SAMESITE", "lax")

def _sign(data: bytes) -> str:
    return hmac.new(SECRET.encode(), data, hashlib.sha256).hexdigest()

def set_session(resp: Response, payload: dict, max_age=60*60*24*7):
    raw = json.dumps({"iat": int(time.time()), **payload}).encode()
    sig = _sign(raw)
    token = base64.urlsafe_b64encode(raw).decode() + "." + sig
    resp.set_cookie(
        COOKIE_NAME, token, max_age=max_age,
        httponly=True, samesite=COOKIE_SAMESITE, secure=COOKIE_SECURE
    )

def get_session(req: Request) -> dict | None:
    token = req.cookies.get(COOKIE_NAME)
    if not token or "." not in token:
        return None
    raw_b64, sig = token.rsplit(".", 1)
    try:
        raw = base64.urlsafe_b64decode(raw_b64.encode())
    except Exception:
        return None
    if _sign(raw) != sig:
        return None
    try:
        return json.loads(raw)
    except Exception:
        return None

def clear_session(resp: Response):
    resp.delete_cookie(COOKIE_NAME)

# --- ADD: FastAPI dependency for current user ---
def get_current_user(req: Request) -> dict:
    sess = get_session(req) or {}
    user_id = sess.get("user_id") or sess.get("id") or (sess.get("user") or {}).get("id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return {**sess, "user_id": user_id}
