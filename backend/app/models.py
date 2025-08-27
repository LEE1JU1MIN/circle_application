# backend/app/models.py

from __future__ import annotations
from datetime import date, datetime, timezone
from sqlalchemy import String, Integer, Boolean, Date, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, declarative_base
from sqlalchemy.dialects.sqlite import JSON
from typing import Optional

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(40), index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    icon: Mapped[Optional[str]] = mapped_column(String(200), default=None)
    login_id: Mapped[str] = mapped_column(String(40), index=True)
    login_pass: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),default=lambda: datetime.now(timezone.utc))


class UserSchedule(Base):
    __tablename__ = "user_schedules"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    circlenews_id: Mapped[int] = mapped_column(Integer, ForeignKey("circle_news.id", ondelete="SET NULL"), index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    start_at: Mapped[date] = mapped_column(Date, nullable=False)
    end_at: Mapped[date] = mapped_column(Date, nullable=False)
    memo: Mapped[Optional[str]] = mapped_column(Text, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),default=lambda: datetime.now(timezone.utc),nullable=False)

class Circle(Base):
    __tablename__ = "circles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),default=lambda: datetime.now(timezone.utc))
    followers: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    image: Mapped[Optional[str]] = mapped_column(String(300), default=None)
    tags: Mapped[list[str]] = mapped_column(JSON, nullable=True)
    sns_links_x: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    sns_links_instagram: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    sns_links_line: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)



class CircleNews(Base):
    __tablename__ = "circle_news"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    circle_id: Mapped[int] = mapped_column(Integer, ForeignKey("circles.id", ondelete="CASCADE"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    content: Mapped[Optional[str]] = mapped_column(Text, default=None)
    has_photo: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    photo_url: Mapped[Optional[str]] = mapped_column(String(300), default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


class Notification(Base):
    __tablename__ = "notifications"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    circle_id: Mapped[int] = mapped_column(Integer, ForeignKey("circles.id", ondelete="CASCADE"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    message: Mapped[Optional[str]] = mapped_column(Text, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

class Followed(Base):
    __tablename__ = "followed"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    circle_id: Mapped[int] = mapped_column(Integer, ForeignKey("circles.id", ondelete="CASCADE"), index=True, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    date: Mapped[Optional[date]] = mapped_column(Date, default=None)



Index("uq_followed_user_circle", Followed.user_id, Followed.circle_id, unique=True)
Index("idx_followed_circle_admin", Followed.circle_id, Followed.is_admin)