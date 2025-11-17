from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from app.core.session import get_current_user

router = APIRouter(tags=["pages"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/me/registrations")
def page_me_registrations(request: Request, current_user=Depends(get_current_user)):
    return templates.TemplateResponse("me_registrations.html", {"request": request, "user": current_user})
