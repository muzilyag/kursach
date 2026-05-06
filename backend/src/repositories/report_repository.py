from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import date
from collections import defaultdict

class ReportRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_seasonality_report(self, year: int):
        query = text("""
            SELECT 
                TO_CHAR(c.content_publish_date, 'TMMonth') AS "month_name",
                EXTRACT(MONTH FROM c.content_publish_date) AS "month_num",
                g.genre_name,
                COUNT(v.content_id) AS "views_count"
            FROM Viewing v
            JOIN Content c ON v.content_id = c.content_id
            JOIN "Is" i ON c.content_id = i.content_id
            JOIN Genre g ON i.genre_id = g.genre_id
            WHERE EXTRACT(YEAR FROM c.content_publish_date) = :year
            GROUP BY "month_name", "month_num", g.genre_name
            ORDER BY "month_num";
        """)

        result = await self.session.execute(query, {"year": year})
        rows = result.mappings().all()

        if not rows:
            return []

        report_dict = defaultdict(dict)
        all_genres = set()

        for row in rows:
            month = row["month_name"].strip()
            genre = row["genre_name"]
            count = row["views_count"]
            
            report_dict[month]["Месяц"] = month
            report_dict[month][genre] = count
            all_genres.add(genre)

        final_report = []
        for month, data in report_dict.items():
            for genre in all_genres:
                if genre not in data:
                    data[genre] = 0
            final_report.append(data)

        return final_report

    async def get_activity_report(self):
        query = text("""
            SELECT 
                st.subscribe_type_name AS "Название подписки",
                COALESCE(
                    ROUND(
                        AVG(
                            EXTRACT(EPOCH FROM (v.viewing_finish - v.viewing_start)) / 60
                        )::numeric, 1
                    ), 0
                ) AS "Среднее время просмотра в день, мин",
                COUNT(DISTINCT v.content_id) AS "Количество уникальных просмотренных фильмов"
            FROM Subscribe_type st
            JOIN Subscribe s ON st.subscribe_type_id = s.subscribe_type_id
            JOIN Viewing v ON s.user_id = v.user_id
            GROUP BY st.subscribe_type_name
            ORDER BY "Количество уникальных просмотренных фильмов" DESC;
        """)

        result = await self.session.execute(query)
        rows = result.mappings().all()
        return [dict(row) for row in rows]

    async def get_revenue_report(self, target_date: date):
        query = text("""
            SELECT 
                st.subscribe_type_name AS "Название подписки",
                COUNT(DISTINCT s.user_id) AS "Количество активных подписок",
                COALESCE(SUM(p.payment_sum), 0) AS "Выручка за месяц, руб"
            FROM Subscribe_type st
            LEFT JOIN Subscribe s ON st.subscribe_type_id = s.subscribe_type_id 
                AND s.subscribe_finish >= CAST(:target_date AS DATE)
            LEFT JOIN Payment p ON st.subscribe_type_id = p.subscribe_type_id 
                AND EXTRACT(MONTH FROM p.payment_date) = EXTRACT(MONTH FROM CAST(:target_date AS DATE))
                AND EXTRACT(YEAR FROM p.payment_date) = EXTRACT(YEAR FROM CAST(:target_date AS DATE))
            GROUP BY st.subscribe_type_name
            ORDER BY "Выручка за месяц, руб" DESC;
        """)

        result = await self.session.execute(query, {"target_date": target_date})
        rows = result.mappings().all()
        return [dict(row) for row in rows]