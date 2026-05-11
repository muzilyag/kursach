from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
import io
import csv
import os
from pathlib import Path
from typing import List, Dict
from decimal import Decimal

from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet

from src.core.database import get_db
from src.repositories.report_repository import ReportRepository

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
FONT_PATH = BASE_DIR / "src" / "static" / "fonts" / "DejaVuSans.ttf"
FONT_BOLD_PATH = BASE_DIR / "src" / "static" / "fonts" / "DejaVuSans-Bold.ttf"

if FONT_PATH.exists() and FONT_BOLD_PATH.exists():
    pdfmetrics.registerFont(TTFont('DejaVuSans', str(FONT_PATH)))
    pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', str(FONT_BOLD_PATH)))
    MAIN_FONT = 'DejaVuSans'
    BOLD_FONT = 'DejaVuSans-Bold'
else:
    MAIN_FONT = 'Helvetica'
    BOLD_FONT = 'Helvetica-Bold'

HEADER_MAP = {
    "subscription": "Подписка",
    "avg time (min)": "Среднее время (мин)",
    "unique content": "Уникальный контент",
    "active subs": "Активные подписки",
    "revenue (rub)": "Выручка (руб.)",
    "month": "Месяц",
    "year": "Год",
    "date": "Дата"
}

MONTH_MAP = {
    "January": "Январь",
    "February": "Февраль",
    "March": "Март",
    "April": "Апрель",
    "May": "Май",
    "June": "Июнь",
    "July": "Июль",
    "August": "Август",
    "September": "Сентябрь",
    "October": "Октябрь",
    "November": "Ноябрь",
    "December": "Декабрь"
}

def process_report_data(data: List[Dict]) -> List[Dict]:
    if not data:
        return data
    
    processed = []
    for row in data:
        new_row = {}
        for key, value in row.items():
            translated_key = HEADER_MAP.get(key.lower(), key)
            
            if isinstance(value, (float, Decimal)):
                new_value = round(float(value), 2)
            elif isinstance(value, str) and value in MONTH_MAP:
                new_value = MONTH_MAP[value]
            else:
                new_value = value
                
            new_row[translated_key] = new_value
        processed.append(new_row)
    return processed

def create_csv_response(data: List[Dict], filename: str):
    if not data:
        raise HTTPException(status_code=404, detail="No data found")
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)
    content = output.getvalue().encode('utf-8-sig')
    return StreamingResponse(
        io.BytesIO(content),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}.csv",
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
    )

def create_pdf_response(data: List[Dict], filename: str, title: str = None):
    if not data:
        raise HTTPException(status_code=404, detail="No data found")
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))
    elements = []

    if title:
        styles = getSampleStyleSheet()
        title_style = styles['Title']
        title_style.fontName = BOLD_FONT
        elements.append(Paragraph(title, title_style))
        elements.append(Spacer(1, 20))

    headers = list(data[0].keys())
    table_data = [headers]
    for item in data:
        table_data.append([str(item.get(h, "")) for h in headers])
    t = Table(table_data)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), BOLD_FONT),
        ('FONTNAME', (0, 1), (-1, -1), MAIN_FONT),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
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
    data = process_report_data(data)
    if export:
        if format == "pdf":
            return create_pdf_response(data, f"seasonality_{year}", title=f"Отчёт по сезонности за {year} год")
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
    data = process_report_data(data)
    if export:
        if format == "pdf":
            return create_pdf_response(data, "activity_report", title="Отчёт по активности пользователей")
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
    data = process_report_data(data)
    if export:
        if format == "pdf":
            formatted_start = start_date.strftime("%d.%m.%Y")
            formatted_end = end_date.strftime("%d.%m.%Y")
            title = f"Отчёт по выручке за период с {formatted_start} по {formatted_end}"
            return create_pdf_response(data, f"revenue_{start_date}_{end_date}", title=title)
        return create_csv_response(data, f"revenue_{start_date}_{end_date}")
    return data