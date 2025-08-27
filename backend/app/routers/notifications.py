from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.db import get_db
from app.models import Notification, User, Circle
from app.schemas import NotificationCreate, NotificationOut

router = APIRouter(prefix="/api/notifications", tags=["notifications"])

def get_current_user_id():
    return 1  # TODO: JWT 인증 후 유저 ID 추출

@router.get("", response_model=list[NotificationOut])
def list_notifications(
    size: int = Query(20, ge=1, le=100),
    user_id: int | None = None,
    db: Session = Depends(get_db)
):
    query = select(Notification).order_by(Notification.id.desc())
    if user_id:
        query = query.where(Notification.user_id == user_id)
    rows = db.execute(query.limit(size)).scalars().all()
    return rows

@router.get("/me", response_model=list[NotificationOut])
def list_my_notifications(
    size: int = Query(20, ge=1, le=100),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    return list_notifications(size=size, user_id=user_id, db=db)

@router.post("", response_model=NotificationOut, status_code=201)
def create_notification(payload: NotificationCreate, db: Session = Depends(get_db)):
    if not db.get(User, payload.user_id):
        raise HTTPException(status_code=404, detail="user not found")
    if not db.get(Circle, payload.circle_id):
        raise HTTPException(status_code=404, detail="circle not found")

    item = Notification(**payload.model_dump())
    db.add(item)
    try:
        db.commit()
        db.refresh(item)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"integrity error: {e}")
    return item

@router.patch("/{id}/read", response_model=NotificationOut, status_code=200)
def mark_as_read(id: int, db: Session = Depends(get_db)):
    row = db.get(Notification, id)
    if not row:
        raise HTTPException(status_code=404, detail="notification not found")
    row.is_read = True
    db.commit()
    return row

@router.delete("/{id}")
def delete_notification(id: int, db: Session = Depends(get_db)):
    row = db.get(Notification, id)
    if not row:
        raise HTTPException(status_code=404, detail="notification not found")
    db.delete(row)
    db.commit()
    return {"ok": True}