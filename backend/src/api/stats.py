from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import asyncio
from src.core.database import get_db

router = APIRouter()

@router.get("")
async def get_stats(db: AsyncSession = Depends(get_db)):
    try:
        queries = [
            db.execute(text('SELECT COUNT(*) FROM "User"')),
            db.execute(text('SELECT COUNT(*) FROM content')),
            db.execute(text('SELECT COUNT(*) FROM subscribe')),
            db.execute(text('SELECT COUNT(*) FROM viewing')),
            db.execute(text("SELECT COUNT(*) FROM subscribe WHERE subscribe_finish >= CURRENT_DATE")),
            db.execute(text("SELECT COALESCE(SUM(payment_sum), 0) as total_revenue FROM payment"))
        ]
        
        results = await asyncio.gather(*queries)
        
        return {
            "users": results[0].scalar() or 0,
            "content": results[1].scalar() or 0,
            "totalSubscriptions": results[2].scalar() or 0,
            "activeSubscriptions": results[3].scalar() or 0,
            "views": results[4].scalar() or 0,
            "totalRevenue": float(results[5].scalar() or 0)
        }
    except Exception as e:
        print(f"Ошибка загрузки статистики: {e}")
        return {
            "users": 0, 
            "content": 0, 
            "totalSubscriptions": 0,
            "activeSubscriptions": 0, 
            "views": 0, 
            "totalRevenue": 0
        }

@router.get("/debug/tables")
async def get_tables_structure(db: AsyncSession = Depends(get_db)):
    tables = ['viewing', 'subscribe', 'User', 'content']
    results = {}
    
    for table in tables:
        table_name_query = table.lower() if table != 'User' else 'User'
        
        query = text("""
            SELECT 
                column_name,
                data_type,
                is_nullable
            FROM information_schema.columns
            WHERE table_name = :table_name
            ORDER BY ordinal_position
        """)
        
        result = await db.execute(query, {"table_name": table_name_query})
        results[table] = result.mappings().all()
        
    return results