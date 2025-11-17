from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, Dict
from app.core.session import get_current_user
from app.services import registrations_service as svc

router = APIRouter(prefix="/api", tags=["registrations"])

@router.get("/me/registrations")
def list_my_registrations(
    status: Optional[str] = Query(None),
    current_user: Dict = Depends(get_current_user),
):
    return svc.list_user_registrations(current_user["user_id"], status_filter=status)

@router.get("/me/registrations/{registration_id}")
def get_my_registration(
    registration_id: str,
    current_user: Dict = Depends(get_current_user),
):
    data = svc.get_registration(registration_id)
    uid_from_id = registration_id.split("_", 1)[-1]
    if uid_from_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    return data

@router.delete("/me/registrations/{event_id}")
def cancel_my_registration(
    event_id: str,
    current_user: Dict = Depends(get_current_user),
):
    try:
        return svc.unregister(event_id, current_user["user_id"])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
