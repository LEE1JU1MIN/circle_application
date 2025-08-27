from fastapi import Depends, HTTPException, Cookie
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db import get_db
from app.models import User
from app.security.singer import parse_session_token   

SESSION_COOKIE = "sid"
SESSION_TTL = 60 * 60 * 24  # 24h

# 현재 유저 세션 존재 검증 (FastAPI cookie사용)
def get_current_user(
    sid: str | None = Cookie(default=None, alias=SESSION_COOKIE),
    db: Session = Depends(get_db),
) -> User:
    if not sid:
        raise HTTPException(status_code=401, detail="not authenticated")
    user_id = parse_session_token(sid, max_age_seconds=SESSION_TTL)
    if not user_id:
        raise HTTPException(status_code=401, detail="session expired or invalid")
    user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="user not found")
    return user