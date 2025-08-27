# app/routers/circle_news.py
from datetime import date
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Circle, CircleNews,Followed,UserSchedule
from app.schemas import CircleNewsOut, CircleNewsCreate

router = APIRouter(
    prefix="/api/circles/{circle_id}/news",
    tags=["circle_news"],
)

# ---------- helpers ----------

def _ensure_circle_exists(db: Session, circle_id: int) -> None:
    exists = db.execute(
        select(Circle.id).where(Circle.id == circle_id)
    ).scalar_one_or_none()
    if not exists:
        raise HTTPException(status_code=404, detail="circle not found")


# ---------- routes ----------

@router.get("", response_model=List[CircleNewsOut])
def list_circle_news(
    circle_id: int,
    size: int = Query(50, ge=1, le=200, description="max number of items"),
    search: Optional[str] = Query(None, description="keyword (title/content)"),
    date_from: Optional[date] = Query(None, description="YYYY-MM-DD start (inclusive)"),
    date_to: Optional[date] = Query(None, description="YYYY-MM-DD end (inclusive)"),
    db: Session = Depends(get_db),
):
    """해당 서클의 뉴스 목록을 간단히 조회합니다."""
    _ensure_circle_exists(db, circle_id)

    stmt = select(CircleNews).where(CircleNews.circle_id == circle_id)

    if search:
        like = f"%{search.strip()}%"
        # content가 NULL일 수도 있으니 title은 확실히 검색, content는 가능할 때만 검색
        stmt = stmt.where(or_(CircleNews.title.ilike(like), CircleNews.content.ilike(like)))

    if date_from:
        stmt = stmt.where(CircleNews.date >= date_from)
    if date_to:
        stmt = stmt.where(CircleNews.date <= date_to)

    # 최신 날짜 우선, 같은 날이면 id 역순
    stmt = stmt.order_by(CircleNews.date.desc(), CircleNews.id.desc()).limit(size)

    try:
        return db.execute(stmt).scalars().all()
    except Exception as e:
        # 쿼리 빌드/파라미터 문제 등
        raise HTTPException(status_code=400, detail=f"query failed: {e}")



@router.post("", response_model=CircleNewsOut, status_code=status.HTTP_201_CREATED)
def create_news(circle_id: int, payload: CircleNewsCreate, db: Session = Depends(get_db)):
    # 0) path/body 일치 검사
    if circle_id != payload.circle_id:
        raise HTTPException(status_code=400, detail="circle_id mismatch between path and body")

    # 1) 뉴스 생성
    news = CircleNews(
        circle_id=payload.circle_id,
        title=payload.title,
        date=payload.date,
        content=payload.content,
        has_photo=payload.has_photo,
        photo_url=payload.photo_url
    )
    db.add(news)
    db.flush() 
    db.refresh(news)  # news.id 필요

    # 2) 팬아웃: 팔로워 → 스케줄 생성
    follower_ids = db.scalars(
        select(Followed.user_id).where(Followed.circle_id == news.circle_id)
    ).all()

    if follower_ids:
        schedules_to_add = [
            UserSchedule(
                user_id=uid,
                circlenews_id=news.id,
                title=news.title,
                start_at=news.date,
                end_at=news.date,
                memo=(news.content or None)
            )
            for uid in follower_ids
        ]
        db.add_all(schedules_to_add)

    # 모든 변경사항을 한 번에 커밋
    try:
        db.commit()
        db.refresh(news)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail=f"unique constraint failed: {getattr(e, 'orig', e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"create news failed: {e}")

    return news


@router.get("/{news_id}", response_model=CircleNewsOut)
def get_circle_news(
    circle_id: int,
    news_id: int,
    db: Session = Depends(get_db),
):
    _ensure_circle_exists(db, circle_id)

    row = db.execute(
        select(CircleNews).where(
            CircleNews.circle_id == circle_id,
            CircleNews.id == news_id
        )
    ).scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="circle_news not found")
    return row


@router.put("/{news_id}", response_model=CircleNewsOut)
def update_circle_news(
    circle_id: int,
    news_id: int,
    payload: CircleNewsCreate,  # 별도의 Update 스키마가 없다면 전체 교체 형태로 유지
    db: Session = Depends(get_db),
):
    _ensure_circle_exists(db, circle_id)

    row = db.execute(
        select(CircleNews).where(
            CircleNews.circle_id == circle_id,
            CircleNews.id == news_id
        )
    ).scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="circle_news not found")

    # circle_id는 경로 기준, 나머지 필드 갱신
    row.title = payload.title
    row.content = payload.content
    row.date = payload.date
    row.has_photo = payload.has_photo

    try:
        db.commit()
        db.refresh(row)
        return row
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"integrity error: {e.orig if hasattr(e, 'orig') else e}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"cannot update circle_news: {e}")


@router.delete("/{news_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_circle_news(
    circle_id: int,
    news_id: int,
    db: Session = Depends(get_db),
):
    _ensure_circle_exists(db, circle_id)

    row = db.execute(
        select(CircleNews).where(
            CircleNews.circle_id == circle_id,
            CircleNews.id == news_id
        )
    ).scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="circle_news not found")

    db.delete(row)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"cannot delete circle_news: {e}")