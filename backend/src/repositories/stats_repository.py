from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class StatsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_dashboard_stats(self):
        users_count = (
            await self.db.execute(text('SELECT COUNT(*) FROM "User"'))
        ).scalar() or 0
        content_count = (
            await self.db.execute(text("SELECT COUNT(*) FROM content"))
        ).scalar() or 0
        total_subs = (
            await self.db.execute(text("SELECT COUNT(*) FROM subscribe"))
        ).scalar() or 0
        active_subs = (
            await self.db.execute(
                text(
                    "SELECT COUNT(*) FROM subscribe WHERE subscribe_finish >= CURRENT_DATE"
                )
            )
        ).scalar() or 0
        views_count = (
            await self.db.execute(text("SELECT COUNT(*) FROM viewing"))
        ).scalar() or 0
        revenue = (
            await self.db.execute(
                text("SELECT COALESCE(SUM(payment_sum), 0) FROM payment")
            )
        ).scalar() or 0

        return {
            "users": users_count,
            "content": content_count,
            "totalSubscriptions": total_subs,
            "activeSubscriptions": active_subs,
            "views": views_count,
            "totalRevenue": float(revenue),
        }

    async def get_tables_structure(self):
        query = text("""
            SELECT table_name, column_name, data_type 
            FROM information_schema.columns 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        result = await self.db.execute(query)
        return [dict(row._mapping) for row in result]
