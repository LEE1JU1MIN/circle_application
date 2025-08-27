# app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db import get_db
from app.models import User
from app.schemas import UserOut, UserCreate
from pydantic import BaseModel, Field
from app.security.security import verify_pw, hash_pw
from app.security.singer import make_session_token
from app.security.auth_deps import SESSION_COOKIE, get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])

class LoginIn(BaseModel):
    login_id: str = Field(..., max_length=50)
    password: str = Field(..., min_length=1)

@router.post("/login", response_model=UserOut)
def login(payload: LoginIn, response: Response, db: Session = Depends(get_db)):
    #일치하는 유저 정보 가져오기
    user = db.execute(select(User).where(User.login_id == payload.login_id)).scalar_one_or_none()

    #1. 아이디가 존재하지 않는경우 
    if not user:
        raise HTTPException(status_code=401, detail="User does not exist")
    #2. 비밀번호가 틀린경우 (해쉬비밀번호 해석)
    if not verify_pw(payload.password, user.login_pass):
        raise HTTPException(status_code=401,detail="Incorrect password")
    
    #만약 아이디/패스워드가 맞다면 토큰 생성
    token = make_session_token(user.id)

    #cookie값 설정 
    response.set_cookie(
        key=SESSION_COOKIE,
        value=token,
        httponly=True,
        secure=False,     # <--- dev. 운영 배포 시 True 로 바꾸기!
        samesite="lax",
        max_age=60 * 60 * 24,
        path="/",
    )

    #cookie값을 가진 user 값 반환
    return user

#로그아웃시, 세션값 삭제 
@router.post("/logout")
def logout(response: Response,):
    response.delete_cookie(SESSION_COOKIE, path="/")
    return {"ok": True}

#get_current_user(세션 존재여부 검사) 실행후 user 값 반환
@router.get("/me", response_model=UserOut)
def me(current: User = Depends(get_current_user)):
    return current

##문제점
#1.세션의 기간이 24시간 -> 재로그인을 해야할 문제도 발생