from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
import io
import csv
from typing import List, Dict

from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

from src.core.database import get_db
from src.repositories.report_repository import ReportRepository

router = APIRouter()

def create_csv_response(data: List[Dict], filename: str):
    if not data:
        raise HTTPException(status_code=404, detail="No data found")
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}.csv",
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
    )

def create_pdf_response(data: List[Dict], filename: str):
    if not data:
        raise HTTPException(status_code=404, detail="No data found")
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))
    elements = []
    headers = list(data[0].keys())
    table_data = [headers]
    for item in data:
        table_data.append([str(item.get(h, "")) for h in headers])
    t = Table(table_data)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(t)
    doc.build(elements)
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}.pdf",
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
    )

@router.get("/seasonality")
async def get_seasonality_report(
    year: int = Query(2022),
    export: bool = Query(False),
    format: str = Query("csv"),
    db: AsyncSession = Depends(get_db)
):
    repo = ReportRepository(db)
    data = await repo.get_seasonality_report(year)
    if export:
        if format == "pdf":
            return create_pdf_response(data, f"seasonality_{year}")
        return create_csv_response(data, f"seasonality_{year}")
    return data

@router.get("/activity")
async def get_activity_report(
    export: bool = Query(False),
    format: str = Query("csv"),
    db: AsyncSession = Depends(get_db)
):
    repo = ReportRepository(db)
    data = await repo.get_activity_report()
    if export:
        if format == "pdf":
            return create_pdf_response(data, "activity_report")
        return create_csv_response(data, "activity_report")
    return data

@router.get("/revenue")
async def get_revenue_report(
    start_date: date = Query(...),
    end_date: date = Query(...),
    export: bool = Query(False),
    format: str = Query("csv"),
    db: AsyncSession = Depends(get_db)
):
    repo = ReportRepository(db)
    data = await repo.get_revenue_report(start_date, end_date)
    if export:
        if format == "pdf":
            return create_pdf_response(data, f"revenue_{start_date}_{end_date}")
        return create_csv_response(data, f"revenue_{start_date}_{end_date}")
    return data