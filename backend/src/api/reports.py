from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
from src.core.database import get_db
from src.repositories.report_repository import ReportRepository

router = APIRouter()

@router.get("/seasonality")
async def get_seasonality_report(
    year: int = Query(2022, description="Год для анализа (в вашей базе это 2022 или 2023)"),
    db: AsyncSession = Depends(get_db)
):
    repo = ReportRepository(db)
    try:
        return await repo.get_seasonality_report(year)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/activity")
async def get_activity_report(
    db: AsyncSession = Depends(get_db)
):
    repo = ReportRepository(db)
    try:
        return await repo.get_activity_report()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/revenue")
async def get_revenue_report(
    target_date: date = Query(..., description="Дата для выбора месяца (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db)
):
    repo = ReportRepository(db)
    try:
        return await repo.get_revenue_report(target_date)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))