from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
import io
import csv
from pathlib import Path
from typing import List, Dict, Optional
from decimal import Decimal
from src.core.security import RoleChecker

from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.legends import Legend

from src.core.database import get_db
from src.repositories.report_repository import ReportRepository

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
FONT_PATH = BASE_DIR / "src" / "static" / "fonts" / "DejaVuSans.ttf"
FONT_BOLD_PATH = BASE_DIR / "src" / "static" / "fonts" / "DejaVuSans-Bold.ttf"

if FONT_PATH.exists() and FONT_BOLD_PATH.exists():
    pdfmetrics.registerFont(TTFont("DejaVuSans", str(FONT_PATH)))
    pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", str(FONT_BOLD_PATH)))
    MAIN_FONT = "DejaVuSans"
    BOLD_FONT = "DejaVuSans-Bold"
else:
    MAIN_FONT = "Helvetica"
    BOLD_FONT = "Helvetica-Bold"

HEADER_MAP = {
    "subscription": "Подписка",
    "avg time (min)": "Среднее время (мин)",
    "unique content": "Уникальный контент",
    "active subs": "Активные подписки",
    "revenue (rub)": "Выручка (руб.)",
    "month": "Месяц",
    "year": "Год",
    "date": "Дата",
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
    "December": "Декабрь",
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
    content = output.getvalue().encode("utf-8-sig")
    return StreamingResponse(
        io.BytesIO(content),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}.csv",
            "Access-Control-Expose-Headers": "Content-Disposition",
        },
    )

def create_pdf_response(data: List[Dict], filename: str, title: str = None, report_type: str = None):
    if not data:
        raise HTTPException(status_code=404, detail="No data found")
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))
    elements = []

    if title:
        styles = getSampleStyleSheet()
        title_style = styles["Title"]
        title_style.fontName = BOLD_FONT
        elements.append(Paragraph(title, title_style))
        elements.append(Spacer(1, 20))

    headers = list(data[0].keys())
    table_data = [headers]
    for item in data:
        table_data.append([str(item.get(h, "")) for h in headers])
    t = Table(table_data)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), BOLD_FONT),
                ("FONTNAME", (0, 1), (-1, -1), MAIN_FONT),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]
        )
    )
    elements.append(t)
    elements.append(Spacer(1, 30))

    if report_type:
        try:
            drawing = Drawing(740, 280)
            
            colors_list = [
                colors.HexColor("#4e79a7"), colors.HexColor("#1cc88a"), 
                colors.HexColor("#36b9cc"), colors.HexColor("#f6c23e"), 
                colors.HexColor("#e74a3b"), colors.HexColor("#858796"),
                colors.HexColor("#5a5c69"), colors.HexColor("#2e59d9")
            ]

            if report_type == "seasonality":
                lc = HorizontalLineChart()
                lc.x = 50
                lc.y = 80
                lc.height = 140
                lc.width = 650
                
                genres = set()
                for row in data:
                    for k in row.keys():
                        if k != "Месяц":
                            genres.add(k)
                genres = sorted(list(genres))
                
                if genres:
                    chart_data = []
                    for genre in genres:
                        line_data = []
                        for row in data:
                            line_data.append(float(row.get(genre, 0)))
                        chart_data.append(line_data)
                        
                    lc.data = chart_data
                    lc.categoryAxis.categoryNames = [str(row.get("Месяц", "")) for row in data]
                    lc.categoryAxis.labels.fontName = MAIN_FONT
                    lc.categoryAxis.labels.angle = 45
                    lc.categoryAxis.labels.dy = -15
                    lc.valueAxis.labels.fontName = MAIN_FONT
                    lc.valueAxis.valueMin = 0
                    lc.lines.symbol = None
                    
                    for i, genre in enumerate(genres):
                        lc.lines[i].strokeColor = colors_list[i % len(colors_list)]
                        lc.lines[i].strokeWidth = 2
                        
                    drawing.add(lc)
                    
                    leg = Legend()
                    leg.fontName = MAIN_FONT
                    leg.alignment = "right"
                    leg.x = 50
                    leg.y = 20
                    leg.columnMaximum = 2
                    leg.colorNamePairs = [(colors_list[i % len(colors_list)], genres[i]) for i in range(len(genres))]
                    drawing.add(leg)
                    
                    elements.append(drawing)

            elif report_type == "activity":
                bc = VerticalBarChart()
                bc.x = 50
                bc.y = 80
                bc.height = 140
                bc.width = 650
                bc.data = [[float(row.get("Среднее время (мин)", 0)) for row in data]]
                bc.categoryAxis.categoryNames = [str(row.get("Подписка", "")) for row in data]
                bc.categoryAxis.labels.fontName = MAIN_FONT
                bc.valueAxis.labels.fontName = MAIN_FONT
                bc.valueAxis.valueMin = 0
                bc.bars[0].fillColor = colors_list[0]
                drawing.add(bc)
                
                leg = Legend()
                leg.fontName = MAIN_FONT
                leg.alignment = "right"
                leg.x = 50
                leg.y = 30
                leg.colorNamePairs = [(colors_list[0], "Среднее время (мин)")]
                drawing.add(leg)
                
                elements.append(drawing)

            elif report_type == "revenue":
                pc_data = [float(row.get("Выручка (руб.)", 0)) for row in data]
                labels = [str(row.get("Подписка", "")) for row in data]
                if sum(pc_data) > 0:
                    pc = Pie()
                    pc.x = 300
                    pc.y = 80
                    pc.width = 140
                    pc.height = 140
                    pc.data = pc_data
                    pc.labels = labels
                    
                    for i in range(len(pc_data)):
                        pc.slices[i].fillColor = colors_list[i % len(colors_list)]
                        pc.slices[i].fontName = MAIN_FONT
                        
                    drawing.add(pc)
                    
                    leg = Legend()
                    leg.fontName = MAIN_FONT
                    leg.alignment = "right"
                    leg.x = 50
                    leg.y = 30
                    leg.columnMaximum = 3
                    leg.colorNamePairs = [(colors_list[i % len(colors_list)], labels[i]) for i in range(len(pc_data))]
                    drawing.add(leg)
                    
                    elements.append(drawing)

        except Exception as e:
            pass

    doc.build(elements)
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}.pdf",
            "Access-Control-Expose-Headers": "Content-Disposition",
        },
    )

@router.get("/seasonality", dependencies=[Depends(RoleChecker(["admin", "superadmin"]))])
async def get_seasonality_report(
    start_month: str = Query(..., pattern=r"^\d{4}-\d{2}$"),
    end_month: str = Query(..., pattern=r"^\d{4}-\d{2}$"),
    export: bool = Query(False),
    format: str = Query("csv"),
    db: AsyncSession = Depends(get_db),
):
    repo = ReportRepository(db)
    data = await repo.get_seasonality_report(start_month, end_month)
    data = process_report_data(data)
    if export:
        if format == "pdf":
            return create_pdf_response(
                data, 
                f"seasonality_{start_month}_to_{end_month}", 
                title=f"Отчёт по сезонности ({start_month} - {end_month})",
                report_type="seasonality"
            )
        return create_csv_response(data, f"seasonality_{start_month}_to_{end_month}")
    return data

@router.get("/activity", dependencies=[Depends(RoleChecker(["admin", "superadmin"]))])
async def get_activity_report(
    subscribe_type_id: Optional[List[int]] = Query(None),
    export: bool = Query(False),
    format: str = Query("csv"),
    db: AsyncSession = Depends(get_db),
):
    repo = ReportRepository(db)
    data = await repo.get_activity_report(subscribe_type_id)
    data = process_report_data(data)
    if export:
        if format == "pdf":
            return create_pdf_response(
                data, 
                "activity_report", 
                title="Отчёт по активности пользователей",
                report_type="activity"
            )
        return create_csv_response(data, "activity_report")
    return data

@router.get("/revenue", dependencies=[Depends(RoleChecker(["admin", "superadmin"]))])
async def get_revenue_report(
    start_date: date = Query(...),
    end_date: date = Query(...),
    export: bool = Query(False),
    format: str = Query("csv"),
    db: AsyncSession = Depends(get_db),
):
    repo = ReportRepository(db)
    data = await repo.get_revenue_report(start_date, end_date)
    data = process_report_data(data)
    if export:
        if format == "pdf":
            formatted_start = start_date.strftime("%d.%m.%Y")
            formatted_end = end_date.strftime("%d.%m.%Y")
            title = f"Отчёт по выручке за период с {formatted_start} по {formatted_end}"
            return create_pdf_response(
                data, 
                f"revenue_{start_date}_{end_date}", 
                title=title,
                report_type="revenue"
            )
        return create_csv_response(data, f"revenue_{start_date}_{end_date}")
    return data