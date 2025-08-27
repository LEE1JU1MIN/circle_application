# app/db.py
from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
import _sqlite3
BASE_DIR = Path(__file__).resolve().parent.parent   # backend/
DATA_DIR = BASE_DIR / "data"                        # backend/data/
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH  = DATA_DIR / "app.sqlite3"                 # backend/data/app.sqlite3

engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False}, echo=True, future=True)

@event.listens_for(engine,"connect")

def set_sqlite_pragma(c, _): 
    cur = c.cursor()
    cur.execute("PRAGMA foreign_keys=ON")
    cur.execute("PRAGMA journal_mode=WAL")
    cur.execute("PRAGMA synchronous=NORMAL")
    cur.close()

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except:
        db.rollback(); 
        raise
    finally:
        db.close()