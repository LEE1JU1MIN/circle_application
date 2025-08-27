# backend/app/schemas.py

from __future__ import annotations
from datetime import datetime, date
from typing import Optional, Dict, List

from pydantic import BaseModel, Field, AnyUrl, EmailStr, field_validator


# 공통: ORM 객체 -> 스키마 변환 허용 (Pydantic v2)
class ORMConfig(BaseModel):
    model_config = {"from_attributes": True}


# =========================
# Users
# =========================

class UserCreate(BaseModel):
    name: str = Field(..., max_length=40)
    email: EmailStr = Field(..., max_length=255)
    icon: Optional[AnyUrl] = Field(None, max_length=200)
    login_id: str = Field(..., min_length=6, max_length=40)
    login_pass: str = Field(..., min_length=6, max_length=200)

class UserOut(ORMConfig):
    id: int
    name: str
    email: EmailStr
    icon: Optional[AnyUrl] = None
    login_id: str
    created_at: datetime

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=40)
    email: Optional[EmailStr] = Field(None, max_length=255)
    icon: Optional[AnyUrl] = Field(None, max_length=200)
    login_id: Optional[str] = Field(None, min_length=6, max_length=40)
    login_pass: Optional[str] = Field(None, min_length=6, max_length=200)


# =========================
# User Schedules
# =========================

class UserScheduleCreate(BaseModel):
    title: str = Field(..., max_length=200)
    start_at: date
    end_at: date
    memo: Optional[str] = None
    schedule_code: str = Field(..., max_length=100)

class UserScheduleOut(ORMConfig):
    id: int
    user_id: int
    circlenews_id: int
    title: str
    start_at: date
    end_at: date
    memo: Optional[str] = None
    created_at: datetime

class UserScheduleUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    start_at: Optional[date] = None
    end_at: Optional[date] = None
    memo: Optional[str] = None
    schedule_code: Optional[str] = Field(None, max_length=100)


# =========================
# Circles
# =========================



class CircleCreate(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    image: Optional[AnyUrl] = Field(None, max_length=300)
    tags: List[str] = Field(default_factory=list)
    sns_links_x:Optional[AnyUrl] = Field(None, max_length=300)
    sns_links_instagram:Optional[AnyUrl] = Field(None, max_length=300)
    sns_links_line:Optional[AnyUrl] = Field(None, max_length=300)
    

class CircleOut(ORMConfig):
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    followers: int
    image: Optional[AnyUrl] = Field(None, max_length=300)
    tags: List[str] = Field(default_factory=list)
    sns_links_x:Optional[AnyUrl] = Field(None, max_length=300)
    sns_links_instagram:Optional[AnyUrl] = Field(None, max_length=300)
    sns_links_line:Optional[AnyUrl] = Field(None, max_length=300)

class CircleUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    image: Optional[AnyUrl] = Field(None, max_length=300)
    tags: Optional[List[str]] = Field(default_factory=list)
    sns_links_x:Optional[AnyUrl] = Field(None, max_length=300)
    sns_links_instagram:Optional[AnyUrl] = Field(None, max_length=300)
    sns_links_line:Optional[AnyUrl] = Field(None, max_length=300)


# =========================
# Circle News
# =========================

class CircleNewsCreate(BaseModel):
    circle_id: int
    title: str = Field(..., max_length=200)
    date: date
    content: Optional[str] = None
    has_photo: bool = False
    photo_url: Optional[str] = Field(None, max_length=300)

class CircleNewsOut(ORMConfig):
    id: int
    circle_id: int
    title: str
    date: date
    content: Optional[str] = None
    has_photo: bool
    created_at: datetime
    photo_url: Optional[str] = Field(None, max_length=300)


# =========================
# Notifications
# =========================

class NotificationCreate(BaseModel):
    user_id: int
    circle_id: int
    title: str = Field(..., max_length=200)
    date: date
    message: Optional[str] = None

class NotificationOut(ORMConfig):
    id: int
    user_id: int
    circle_id: int
    title: str
    date: date
    message: Optional[str] = None
    created_at: datetime


# =========================
# Followed
# =========================

class FollowedCreate(BaseModel):
    user_id: int
    circle_id: int
    date: Optional[date] = None
    is_admin: bool = False

class FollowedOut(ORMConfig):
    id: int
    user_id: int
    circle_id: int
    date: Optional[date] = None
    is_admin: bool