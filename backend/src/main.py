from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from src.core.database import AsyncSessionLocal
from src.api import users, content, reports, subscriptions, stats
from src.core.config import settings

app = FastAPI(title="Online Cinema API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.cors_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(content.router, prefix="/api/content", tags=["Content"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
app.include_router(subscriptions.router, prefix="/api/subscriptions", tags=["Subscriptions"])
app.include_router(stats.router, prefix="/api/stats", tags=["Admin & Stats"])

@app.get("/api/health", tags=["System"])
async def health_check():
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT NOW()"))
            timestamp = result.scalar()
            return {
                "status": "OK",
                "database": "Connected",
                "timestamp": timestamp
            }
    except Exception as e:
        return {
            "status": "ERROR",
            "message": str(e)
        }