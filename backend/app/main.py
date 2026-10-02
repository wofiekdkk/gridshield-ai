"""
GridShield AI - FastAPI Main Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.logger import logger
from app.database.session import init_db, SessionLocal, store
from app.api.v1.router import api_router
from app.models.db_models import User, UserRole
from app.core.security import hash_password


def seed_admin():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        existing_names = [u.get("username") for u in users]

        if "admin" not in existing_names:
            db.add(User(
                username="admin",
                email="admin@gridshield.ai",
                hashed_password=hash_password("admin123"),
                role="ADMIN",
                is_active=True,
            ))
        if "operator" not in existing_names:
            db.add(User(
                username="operator",
                email="operator@gridshield.ai",
                hashed_password=hash_password("operator123"),
                role="OPERATOR",
                is_active=True,
            ))
        if "viewer" not in existing_names:
            db.add(User(
                username="viewer",
                email="viewer@gridshield.ai",
                hashed_password=hash_password("viewer123"),
                role="VIEWER",
                is_active=True,
            ))
        db.commit()
        logger.info("Default security roles seeded: admin, operator, viewer.")
    except Exception as e:
        logger.error(f"Seed error: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=" * 60)
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info("=" * 60)
    init_db()
    seed_admin()
    yield
    logger.info("Backend shutting down.")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
def root():
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational",
        "docs": "/docs",
        "api": settings.API_V1_PREFIX,
    }


@app.get("/health")
def health():
    return {"status": "healthy", "service": settings.APP_NAME}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
