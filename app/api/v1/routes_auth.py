# app/api/v1/routes_auth.py
from fastapi import APIRouter, Form, Response, Request, HTTPException
from typing import Optional, Literal
from app.services.auth_service import login_user, register_user
from app.schemas.user import UserResponse
from app.core.session import set_session, get_session, clear_session
from typing import Optional, Literal
router = APIRouter(tags=["auth"])
UserType = Literal["student", "user"]

@router.post("/login")
@router.post("/auth/login")
def login(
    response: Response,
    user_type: UserType = Form(...),
    student_id: Optional[str] = Form(None),
    citizen_id: Optional[str] = Form(None),
    identifier: Optional[str] = Form(None),
    password: Optional[str] = Form(None),
):
    user = login_user(
        user_type=user_type,
        identifier=identifier,
        password=password,
        student_id=student_id,
        citizen_id=citizen_id,
    )
    if not user or not user.get("user_id"):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # 👇 เก็บ role ลง session เพื่อให้หน้า/ API แยกสิทธิ์ได้
    set_session(response, {
        "user_id": user["user_id"],
        "display_name": user.get("full_name") or user.get("username") or user["user_id"],
        "role": user.get("role", "other"),
        "username": user.get("username") or user["user_id"],
    })
    return {"ok": True, "message": user.get("message", "Login success")}

@router.post("/register", response_model=UserResponse)
@router.post("/auth/register", response_model=UserResponse)
def register(
    username: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    email: str = Form(...),
    grade: str = Form(...),
    phone_num: str = Form(...),
    role: str = Form("other"),
    firstname: str = Form(...),
    lastname: str = Form(...),
):
    return register_user(
        username, password, confirm_password, email,
        grade, phone_num, role, firstname, lastname
    )

@router.get("/me")
@router.get("/auth/me")
def me(request: Request):
    sess = get_session(request)
    if not sess:
        raise HTTPException(status_code=401, detail="Not logged in")
    return {
        "user_id": sess["user_id"],
        "display_name": sess.get("display_name", ""),
        "role": sess.get("role", "other"),
        "username": sess.get("username"),
    }

@router.post("/logout")
@router.post("/auth/logout")
def logout(response: Response):
    clear_session(response)
    return {"ok": True}
