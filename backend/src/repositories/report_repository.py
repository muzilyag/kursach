from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import date

class ReportRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_activity_report(self, start_date: date, end_date: date):
        query = text("""
            SELECT 
                COALESCE(st.subscribe_type_name, 'ИТОГО / СРЕДНЕЕ') as "Тип подписки",
                COUNT(DISTINCT v.user_id) as "Кол-во пользователей",
                ROUND(AVG(v.viewing_progress), 1) as "Средний прогресс (%)",
                COUNT(v.content_id) as "Всего просмотров"
            FROM viewing v
            JOIN subscribe s ON v.user_id = s.user_id
            JOIN subscribe_type st ON s.subscribe_type_id = st.subscribe_type_id
            WHERE v.viewing_start::date BETWEEN :start_date AND :end_date
            GROUP BY ROLLUP(st.subscribe_type_name)
            ORDER BY st.subscribe_type_name NULLS LAST;
        """)

        result = await self.session.execute(query, {
            "start_date": start_date,
            "end_date": end_date
        })
        
        rows = result.mappings().all()
        return [dict(row) for row in rows]