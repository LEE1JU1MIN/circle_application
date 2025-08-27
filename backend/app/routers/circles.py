# app/routers/circles.py
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db import get_db
from app.models import Circle
from app.schemas import CircleCreate, CircleUpdate, CircleOut

router = APIRouter(prefix="/api/circles", tags=["circles"])


# -----------------------------
# helpers
# -----------------------------
def _to_circle_out(row: Circle) -> Dict[str, Any]:
    """Map ORM(Circle) -> CircleOut(dict). Handles field-name mismatch and defaults."""
    return {
        "id": row.id,
        "name": row.name,
        "description": row.description,
        "created_at": row.created_at,
        "followers": row.followers,
        "image": row.image,
        "tags": row.tags or [],
        "sns_links_x": row.sns_links_x,
        "sns_links_instagram": row.sns_links_instagram,
        "sns_links_line": row.sns_links_line,
    }


@router.get("", response_model=List[CircleOut])
def list_circles(
    size: int = Query(20, ge=1, le=100, description="size"),
    db: Session = Depends(get_db),
):
    q = select(Circle).limit(size)
    
    try:
        circle = db.execute(q).scalars().all()
        return circle
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"query is invailed: {e}")



@router.post("", response_model=CircleOut, status_code=status.HTTP_201_CREATED)
def create_circle(payload: CircleCreate, db: Session = Depends(get_db)):

    circle = payload.model_dump()
    circle["name"] = str(circle["name"]).strip()
    if circle.get("image"):
        circle["image"] = str(circle["image"])
    if circle.get("sns_links_x"):
        circle["sns_links_x"] = str(circle["sns_links_x"])
    if circle.get("sns_links_instagram"):
        circle["sns_links_instagram"] = str(circle["sns_links_instagram"])
    if circle.get("sns_links_line"):
        circle["sns_links_line"] = str(circle["sns_links_line"])

    circle = Circle(**circle)

    db.add(circle)
    try:
        db.commit()
        db.refresh(circle)
        return circle
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="circle name already exists")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"cannot create circle: {e}")



@router.get("/{circle_id}", response_model=CircleOut)
def get_circle(circle_id: int, db: Session = Depends(get_db)):
    row = db.get(Circle, circle_id)
    if not row:
        raise HTTPException(status_code=404, detail="circle not found")
    return _to_circle_out(row)



@router.put("/{circle_id}", response_model=CircleOut)
def update_circle(circle_id: int, payload: CircleUpdate, db: Session = Depends(get_db)):
    row = db.get(Circle, circle_id)
    if not row:
        raise HTTPException(status_code=404, detail="circle not found")

    update_data = payload.model_dump(exclude_unset=True)

    if update_data.get("image"):
        update_data["image"] = str(update_data["image"])
        
    if update_data.get("sns_links_x"):
        update_data["sns_links_x"] = str(update_data["sns_links_x"])
    
    if update_data.get("sns_links_instagram"):
        update_data["sns_links_instagram"] = str(update_data["sns_links_instagram"])

    if update_data.get("sns_links_line"):
        update_data["sns_links_line"] = str(update_data["sns_links_line"])
    

    for key, value in update_data.items():
        setattr(row, key, value)
    
    try:
        db.commit()
        db.refresh(row)
        return row
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="circle name already exists")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"cannot update circle: {e}")



@router.delete("/{circle_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_circle(circle_id: int, db: Session = Depends(get_db)):
    row = db.get(Circle, circle_id)
    if not row:
        raise HTTPException(status_code=404, detail="circle not found")

    db.delete(row)
    try:
        db.commit()
        return  
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"cannot delete circle: {e}")