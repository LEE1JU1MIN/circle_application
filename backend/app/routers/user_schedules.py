from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db import get_db
from app.models import UserSchedule, User
from app.schemas import UserScheduleOut, UserScheduleCreate, UserScheduleUpdate
from app.security.auth_deps import get_current_user


router = APIRouter(prefix="/api/user_schedules", tags=["user_schedules"])


@router.get("", response_model=list[UserScheduleOut])
def list_my_schedules(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    
    stmt = (
        select(UserSchedule)
        .where(UserSchedule.user_id == current_user.id) #유저 검증 
        .order_by(UserSchedule.start_at.asc()) #start_at 오름차순정렬
    )
    schedules = db.execute(stmt).scalars().all() #DB에서 스케쥴 리스트 생성
    return schedules



@router.post("", response_model=UserScheduleOut, status_code=201)
def create_my_schedule(
    payload: UserScheduleCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data = payload.model_dump()
    item = UserSchedule(user_id=current_user.id, **data) #새로운 스케쥴 생성
    db.add(item) #스케쥴 DB에 추가
    
    try:
        db.commit()
        db.refresh(item)
        return item
    
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Cannot create schedule")

@router.delete("/{schedule_id}", status_code=204)
def delete_my_schedule(
    schedule_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    #유저 검증/스케쥴 검증
    stmt = (select(UserSchedule)
            .where(UserSchedule.id == schedule_id,UserSchedule.user_id == current_user.id)
            )
    
    row = db.execute(stmt).scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    db.delete(row)
    db.commit()


##문제점
#1.서클에서 생성된 뉴스를 자동으로 유저 스케쥴에 삽입이 안됨
