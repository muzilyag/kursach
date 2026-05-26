from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from src.core.database import AsyncSessionLocal
from src.api import (
    users,
    content,
    reports,
    subscriptions,
    stats,
    auth,
    tags,
    copyright_holders,
    advertising,
)
from src.core.config import settings

app = FastAPI(title="Online Cinema API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(content.router, prefix="/api/v1/content", tags=["Content"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])
app.include_router(
    subscriptions.router, prefix="/api/v1/subscriptions", tags=["Subscriptions"]
)
app.include_router(stats.router, prefix="/api/v1/stats", tags=["Admin & Stats"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(tags.router, prefix="/api/v1/tags", tags=["Tags"])
app.include_router(
    copyright_holders.router,
    prefix="/api/v1/copyright-holders",
    tags=["Copyright Holders"],
)
app.include_router(
    advertising.router, prefix="/api/v1/advertising", tags=["Advertising"]
)


@app.get("/api/v1/health", tags=["System"])
async def health_check():
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT NOW()"))
            timestamp = result.scalar()
            return {"status": "OK", "database": "Connected", "timestamp": timestamp}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}
