from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import date

class ReportRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_seasonality_report(self, year: int):
        query = text("""
            WITH RECURSIVE months AS (
                SELECT 1 as m UNION ALL SELECT m + 1 FROM months WHERE m < 12
            ),
            all_genres AS (
                SELECT genre_id, genre_name FROM Genre
            ),
            calendar_grid AS (
                SELECT m, genre_id, genre_name FROM months CROSS JOIN all_genres
            ),
            stats AS (
                SELECT 
                    EXTRACT(MONTH FROM v.viewing_start) as m,
                    i.genre_id,
                    COUNT(*) as cnt
                FROM Viewing v
                JOIN "Is" i ON v.content_id = i.content_id
                WHERE EXTRACT(YEAR FROM v.viewing_start) = :year
                GROUP BY m, i.genre_id
            )
            SELECT 
                TRIM(TO_CHAR(TO_DATE(cg.m::text, 'MM'), 'Month')) as month_name,
                cg.m as month_num,
                cg.genre_name,
                COALESCE(s.cnt, 0) as views_count
            FROM calendar_grid cg
            LEFT JOIN stats s ON cg.m = s.m AND cg.genre_id = s.genre_id
            ORDER BY cg.m, cg.genre_name;
        """)
        
        result = await self.session.execute(query, {"year": year})
        rows = result.mappings().all()

        report_data = {}
        for row in rows:
            m_name = row["month_name"]
            if m_name not in report_data:
                report_data[m_name] = {"month": m_name, "_order": row["month_num"]}
            report_data[m_name][row["genre_name"]] = row["views_count"]

        sorted_report = sorted(report_data.values(), key=lambda x: x["_order"])
        for item in sorted_report:
            item.pop("_order")
        
        return sorted_report

    async def get_activity_report(self):
        query = text("""
            WITH sub_activity AS (
                SELECT 
                    s.subscribe_type_id,
                    AVG(EXTRACT(EPOCH FROM (v.viewing_finish - v.viewing_start)) / 60) as avg_time,
                    COUNT(DISTINCT v.content_id) as unique_content
                FROM Subscribe s
                JOIN Viewing v ON s.user_id = v.user_id
                GROUP BY s.subscribe_type_id
            )
            SELECT 
                st.subscribe_type_name AS "Subscription",
                COALESCE(ROUND(AVG(sa.avg_time)::numeric, 1), 0) AS "Avg Time (min)",
                COALESCE(SUM(sa.unique_content), 0) AS "Unique Content"
            FROM Subscribe_type st
            LEFT JOIN sub_activity sa ON st.subscribe_type_id = sa.subscribe_type_id
            GROUP BY st.subscribe_type_name
            ORDER BY "Unique Content" DESC;
        """)
        result = await self.session.execute(query)
        return [dict(row) for row in result.mappings().all()]

    async def get_revenue_report(self, start_date: date, end_date: date):
        query = text("""
            WITH active_counts AS (
                SELECT 
                    subscribe_type_id, 
                    COUNT(DISTINCT user_id) as active_cnt
                FROM Subscribe
                WHERE subscribe_start <= :end_date AND subscribe_finish >= :start_date
                GROUP BY subscribe_type_id
            ),
            period_payments AS (
                SELECT 
                    subscribe_type_id as sub_id, 
                    SUM(payment_sum) as total_rev
                FROM Payment
                WHERE payment_date >= :start_date AND payment_date <= :end_date
                GROUP BY subscribe_type_id
            )
            SELECT 
                st.subscribe_type_name AS "Subscription",
                COALESCE(SUM(ac.active_cnt), 0) AS "Active Subs",
                COALESCE(SUM(pp.total_rev), 0) AS "Revenue (RUB)"
            FROM Subscribe_type st
            LEFT JOIN active_counts ac ON st.subscribe_type_id = ac.subscribe_type_id
            LEFT JOIN period_payments pp ON st.subscribe_type_id = pp.sub_id
            GROUP BY st.subscribe_type_name
            ORDER BY "Revenue (RUB)" DESC;
        """)
        result = await self.session.execute(query, {"start_date": start_date, "end_date": end_date})
        return [dict(row) for row in result.mappings().all()]