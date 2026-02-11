from fastapi import FastAPI
from .config import settings
from .db import Base, engine
from .routes_auth import router as auth_router
from .routes_users import router as users_router
from .routes_admin import router as admin_router

def create_app() -> FastAPI:
    app = FastAPI(title=settings.APP_NAME)

    # Create tables (for day-1 demo). In real prod, use Alembic migrations.
    Base.metadata.create_all(bind=engine)

    app.include_router(auth_router)
    app.include_router(users_router)
    app.include_router(admin_router)

    @app.get("/health")
    def health():
        return {"status": "ok", "app": settings.APP_NAME}

    return app

app = create_app()
