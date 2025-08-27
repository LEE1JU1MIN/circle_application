# app/routers/user.py 
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from typing import List

from app.db import get_db
from app.models import User
from app.schemas import UserCreate, UserUpdate, UserOut
from app.security.security import hash_pw


router = APIRouter(prefix="/api/user", tags=["user"])


@router.get("", response_model=List[UserOut])
def list_user(
    size: int = Query(20, ge=1, le=100, description="size of user"),
    search: str | None = Query(None, description="name/email/loginId"),
    sort: str = Query("-id", description="sorted by: id|name|created_at, '-'decresed"),
    db: Session = Depends(get_db),
):
    
    q = select(User)

        #search 탐색
    if search:
            s = f"%{search.strip().lower()}%"
            q = q.where(or_(
                func.lower(User.name).like(s),
                func.lower(User.email).like(s),
                func.lower(User.login_id).like(s),
            ))
        
        # 정렬
    sort_map = {"id": User.id, "name": User.name, "created_at": User.created_at}
    desc = sort.startswith("-")

    key = sort[1:] if desc else sort
  
    col = sort_map.get(key, User.id) #key값으로 탐색 (디폴트 id)

    q = q.order_by(col.desc() if desc else col.asc()).limit(size)

    try:
        user = db.execute(q).scalars().all()
        return user
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Query is not working: {e}")



@router.post("", response_model=UserOut, status_code=201)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    
    user = payload.model_dump()
    if user.get("icon"):
        user["icon"] = str(user["icon"])
    user["login_pass"] = hash_pw(user["login_pass"])
    user = User(**user)

    db.add(user)
    try:
        db.commit()
        db.refresh(user)
        return user
    
    except IntegrityError:
        db.rollback()
        # 이메일 또는 login_id의 UNIQUE 제약 조건 위반 시 409 반환
        raise HTTPException(
            status_code=409,detail="email or login id is already exist.")



@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Cannot find the user")
    return user



@router.put("/{user_id}", response_model=UserOut)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code= 404, detail="Cannot find the user")

    # Pydantic이 None이 아닌 값들만 덤프 (exclude_unset=True)
    updated_user = payload.model_dump(exclude_unset=True)
    if not updated_user:
        return user

    if updated_user.get("icon"):
        updated_user["icon"] = str(updated_user["icon"]) 
    
    if updated_user.get("login_pass"):
        updated_user["login_pass"] = hash_pw(updated_user["login_pass"])

    for key, value in updated_user.items():
        setattr(user, key, value)
    
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
        return user
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="email or login_id is already exist")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"User update failed: {e}")



@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Cannot find the user")
    
    db.delete(user)
    db.commit()

