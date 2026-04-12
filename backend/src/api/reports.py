from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
from src.core.database import get_db
from src.repositories.report_repository import ReportRepository

router = APIRouter()

@router.get("/activity")
async def get_activity_report(
    start_date: date = Query(..., description="Начальная дата (YYYY-MM-DD)"),
    end_date: date = Query(..., description="Конечная дата (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db)
):
    if start_date > end_date:
        raise HTTPException(
            status_code=400, 
            detail="Дата начала должна быть раньше даты окончания"
        )
        
    repo = ReportRepository(db)
    
    try:
        report_data = await repo.get_activity_report(start_date, end_date)
        return report_data
    except Exception as e:
        print(f"Ошибка при генерации отчёта: {e}")
        return []