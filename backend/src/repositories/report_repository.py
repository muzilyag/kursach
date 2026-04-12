from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import date

class ReportRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_activity_report(self, start_date: date, end_date: date):
        query = text("""
            WITH active_subscriptions AS (
                SELECT DISTINCT 
                    s.user_id,
                    s.subscribe_type_id,
                    st.subscribe_type_name
                FROM subscribe s
                JOIN subscribe_type st ON s.subscribe_type_id = st.subscribe_type_id
                WHERE s.subscribe_start <= :end_date 
                    AND s.subscribe_finish >= :start_date
            ),
            all_views AS (
                SELECT 
                    v.user_id,
                    v.viewing_progress,
                    c.content_duration
                FROM viewing v
                JOIN content c ON v.content_id = c.content_id
            ),
            user_metrics AS (
                SELECT 
                    v.user_id,
                    AVG(v.viewing_progress) as avg_progress,
                    COUNT(v.user_id) as total_views,
                    AVG(EXTRACT(EPOCH FROM c.content_duration)/60 * (v.viewing_progress / 100.0)) as avg_time_min
                FROM all_views v
                GROUP BY v.user_id
            )
            SELECT 
                a.subscribe_type_name as "Тип подписки",
                COUNT(DISTINCT a.user_id) as "Количество пользователей",
                COALESCE(ROUND(AVG(m.avg_progress)::numeric, 2), 0) as "Средний прогресс просмотра (%)",
                COALESCE(SUM(m.total_views), 0) as "Всего просмотров",
                COALESCE(ROUND(AVG(m.avg_time_min)::numeric, 2), 0) as "Среднее время (мин)"
            FROM active_subscriptions a
            LEFT JOIN user_metrics m ON a.user_id = m.user_id
            GROUP BY a.subscribe_type_name
            ORDER BY "Количество пользователей" DESC
        """)
        
        result = await self.session.execute(query, {
            "start_date": start_date, 
            "end_date": end_date
        })
        return result.mappings().all()