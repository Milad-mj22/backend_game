from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import engine, Base, SessionLocal
from app.models import city, neighborhood, user, activity, badge, clan  # noqa: F401
from app.routers import city as city_router
from app.routers import neighborhood as neighborhood_router
from app.routers import auth as auth_router
from app.routers import activity as activity_router
from app.routers import badge as badge_router
from app.routers import clan as clan_router
from app.routers import leaderboard as leaderboard_router
from app.services import badge_service, city_service
from app.routers import my_neighborhood as my_neighborhood_router


Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = SessionLocal()
    try:
        badge_service.seed_badges(db)
        city_service.seed_cities(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="Walk Project API",
    description="API برای سیستم پیاده‌روی و گیمیفیکیشن",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

app.include_router(auth_router.router)
app.include_router(city_router.router)
app.include_router(neighborhood_router.router)
app.include_router(activity_router.router)
app.include_router(badge_router.router)
app.include_router(clan_router.router)
app.include_router(leaderboard_router.router)
app.include_router(my_neighborhood_router.router)

@app.get("/")
def read_root():
    return {"message": "سلام به دنیای FastAPI حرفه‌ای"}