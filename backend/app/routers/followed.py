from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.db import get_db
from app.models import Followed, User, Circle
from app.schemas import FollowedCreate, FollowedOut
from app.security.auth_deps import get_current_user


router = APIRouter(prefix="/api/followed", tags=["followed"])

@router.get("", response_model=list[FollowedOut])
def list_all_followed_circles(
    db: Session = Depends(get_db)
):

    stmt = (
        select(Followed)
        .order_by(Followed.id.desc())
    )
    rows = db.execute(stmt).scalars().all()
    return rows


@router.get("/current_user", response_model=list[FollowedOut])
def list_my_followed_circles(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    stmt = (
        select(Followed)
        .where(Followed.user_id == current_user.id)
        .order_by(Followed.id.desc())
    )
    return db.execute(stmt).scalars().all()


@router.post("", response_model=FollowedOut)
def create_Followed(
    payload: FollowedCreate, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    
    data = payload.model_dump()
    data["user_id"] = current_user.id

    circle = db.execute(select(Circle.id).where(
        Circle.id == payload.circle_id)
        ).scalar_one_or_none()
    
    if not circle:
        raise HTTPException(status_code=404, detail="circle not found")

    # 重複チェックは current_user.id を使う
    dup = db.execute(
        select(Followed.id).where(
            Followed.user_id == current_user.id,
            Followed.circle_id == payload.circle_id
        )
    ).scalar_one_or_none()
    if dup:
        raise HTTPException(status_code=409, detail="already joined")

    # 正しい user_id を含めて一度だけ作成
    followed = Followed(**data)

    db.add(followed)
    try:
        db.commit()
        db.refresh(followed)
        return followed
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail="integrity error")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"cannot create Followed: {e}")



@router.delete("/{circle_id}", status_code=204)
def delete_Followed(
    circle_id: int, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):

    stmt = select(Followed).where(
        Followed.user_id == current_user.id, 
        Followed.circle_id == circle_id
    )
    row = db.execute(stmt).scalar_one_or_none()

    if not row:
        raise HTTPException(status_code=404, detail="Followed relationship not found")
    
    db.delete(row)
    db.commit()
