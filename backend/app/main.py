from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db import engine,DB_PATH
from app.models import Base
from app.routers import users, user_schedules, circles,circle_news,notifications,followed, auth
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)  
    print("DB_PATH =>", DB_PATH)
    yield

app = FastAPI(title="DB App", lifespan=lifespan)
app.include_router(users.router)
app.include_router(user_schedules.router)
app.include_router(circles.router)
app.include_router(notifications.router)  
app.include_router(followed.router)  
app.include_router(circle_news.router)
app.include_router(auth.router) 

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    # "https://www.your-frontend.com",  # 배포 시 여기에 운영 도메인 추가
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "ok"}

