import traceback
from pathlib import Path
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.db.firebase import initialize_firebase, get_db
from app.repositories import events_repo

# --- Routers ---
from app.api.v1.routes_auth import router as auth_router
from app.api.v1.routes_student import router as student_router
from app.api.v1.routes_events import router as events_router
from app.api.v1.routes_admin import router as admin_router
from app.api.v1.routes_registrations import router as registrations_router
from app.api.v1.routes_pages import router as pages_router
from app.api.v1 import routes_admin_users
from app.api.v1 import routes_uploads

templates = Jinja2Templates(directory="templates")

def status_label(v):
    s = getattr(v, "value", None) or getattr(v, "name", None) or str(v)
    s = s.split(".")[-1]
    mapping = {"OPEN":"Open", "CLOSE":"Close", "FULL":"Full", "UPCOMING":"Upcoming"}
    return mapping.get(s.upper(), s)

templates.env.filters["status_label"] = status_label

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        initialize_firebase()
    except Exception as e:
        print(f"[startup] Firebase init failed: {e!r}")
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    debug=settings.DEBUG,
    version="1.0.0",
    lifespan=lifespan,
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "type": type(exc).__name__, "path": str(request.url)},
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# --- Include routers (หนึ่งครั้ง ไม่ซ้ำ) ---
app.include_router(auth_router,          prefix=settings.API_PREFIX)
app.include_router(student_router,       prefix=settings.API_PREFIX)
app.include_router(events_router,        prefix=settings.API_PREFIX)
app.include_router(admin_router,         prefix=settings.API_PREFIX)
app.include_router(registrations_router)  # already prefixed with /api in file
app.include_router(pages_router)          # server-rendered pages
app.include_router(routes_admin_users.router)
app.include_router(routes_uploads.router, prefix=settings.API_PREFIX)

# ---------- Pages ----------
from app.core.session import get_session

def _require_admin_session(request: Request):
    sess = get_session(request)
    if not sess or sess.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    return sess

@app.get("/admin", response_class=HTMLResponse, tags=["pages"], name="admin_home")
def admin_home(request: Request):
    _require_admin_session(request)
    return templates.TemplateResponse("admin/dashboard.html", {"request": request})

@app.get("/admin/events", response_class=HTMLResponse, tags=["pages"], name="admin_events_page")
def admin_events_page(request: Request):
    _require_admin_session(request)
    return templates.TemplateResponse("admin/events.html", {"request": request})

@app.get("/", response_class=HTMLResponse, tags=["pages"])
def root_page():
    return RedirectResponse(url="/auth", status_code=302)

@app.get("/auth", response_class=HTMLResponse, tags=["pages"], name="auth_page")
def serve_auth_page(request: Request):
    return templates.TemplateResponse(
        "auth.html",
        {"request": request, "app_name": settings.PROJECT_NAME, "env": settings.ENV},
    )

@app.get("/main", response_class=HTMLResponse, tags=["pages"], name="main_page")
def main_page(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})

def _serialize(doc):
    d = doc.to_dict() or {}
    d["event_id"] = doc.id
    if "major" not in d and "location" in d and d.get("location"):
        d["major"] = d["location"]

    def _to_iso(val):
        try:
            if hasattr(val, "isoformat"):
                return val.isoformat()
        except Exception:
            pass
        return val

    for k in ("event_date", "deadline_date", "created_at", "updated_at"):
        if k in d:
            d[k] = _to_iso(d[k])

    val = d.get("status", "")
    if isinstance(val, list):
        d["status"] = val[0] if val else ""
    elif val is None:
        d["status"] = ""
    else:
        d["status"] = str(val)

    return d

@app.get("/events", response_class=HTMLResponse, tags=["pages"], name="events_page")
def events_page(request: Request):
    try:
        events = events_repo.list_events(limit=200)

        def to_iso(x):
            return x.isoformat() if hasattr(x, "isoformat") else x

        items = []
        for ev in events:
            d = ev.model_dump()
            s = getattr(ev, "status", None)
            if s is not None and not isinstance(s, str):
                d["status"] = getattr(s, "value", str(s))
            for k in ("event_date", "deadline_date", "created_at", "updated_at", "register_open_at"):
                if k in d and d[k] is not None:
                    d[k] = to_iso(d[k])
            items.append(d)

        return templates.TemplateResponse("events/events.html", {"request": request, "items": items})
    except Exception as e:
        traceback.print_exc()
        return HTMLResponse(
            f"""<h3>Internal error at /events</h3>
                <p>{type(e).__name__}: {e}</p>
                <p>ดูรายละเอียดที่ server log (stacktrace)</p>""",
            status_code=500
        )

@app.get("/events/{event_id}", response_class=HTMLResponse, tags=["pages"], name="detail_event_page")
def detail_event_page(event_id: str, request: Request):
    db = get_db()
    snap = db.collection("events").document(event_id).get()
    if not snap.exists:
        raise HTTPException(status_code=404, detail="Event not found")
    ev = _serialize(snap)
    return templates.TemplateResponse("events/detail.html", {"request": request, "ev": ev})

# ---------- Health ----------
@app.get("/health", tags=["ops"])
def health_check():
    ok: bool = False
    info: Optional[str] = None
    try:
        db = get_db()
        _ = db.project
        ok = True
    except Exception as e:
        ok = False
        info = repr(e)

    return {
        "status": "healthy" if ok else "degraded",
        "firebase_connected": ok,
        "env": settings.ENV,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "info": info,
    }

@app.get("/admin/users", response_class=HTMLResponse, tags=["pages"], name="admin_users_page")
def admin_users_page(request: Request):
    _require_admin_session(request)
    return templates.TemplateResponse("admin/admin_user.html", {"request": request})


