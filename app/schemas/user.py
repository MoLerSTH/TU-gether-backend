# app/schemas/user.py
from typing import Optional, Annotated
from pydantic import BaseModel, EmailStr, Field

# --- Type aliases ด้วย Annotated ---
Username = Annotated[str, Field(min_length=3, max_length=50)]
Password = Annotated[str, Field(min_length=8, max_length=12, pattern=r"^\S+$")]
PhoneNumber = Annotated[str, Field(pattern=r"^\d{10}$")]

class UserRegistration(BaseModel):
    username: Username
    password: Password
    confirm_password: Password
    email: EmailStr
    grade: int
    phone_num: PhoneNumber
    role: str = "other"
    firstname: str
    lastname: str

class UserOut(BaseModel):
    user_id: str
    username: str
    email: EmailStr
    full_name: str
    role: str
    grade: Optional[int] = None
    phone_num: Optional[str] = None

class UserResponse(BaseModel):
    message: str
    username: str
