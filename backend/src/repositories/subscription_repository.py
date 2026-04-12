from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import date
from typing import Optional

class SubscriptionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_subscriptions(self, page: int = 1, limit: int = 10, start_date: Optional[date] = None, end_date: Optional[date] = None):
        offset = (page - 1) * limit
        
        where_clauses = []
        params = {"limit": limit, "offset": offset}
        
        if start_date:
            where_clauses.append("s.subscribe_start >= :start_date")
            params["start_date"] = start_date
        if end_date:
            where_clauses.append("s.subscribe_start <= :end_date")
            params["end_date"] = end_date
            
        where_sql = " AND ".join(where_clauses)
        if where_sql:
            where_sql = f"WHERE {where_sql}"
            
        query = text(f"""
            SELECT 
                ROW_NUMBER() OVER (ORDER BY s.subscribe_start DESC) as "#",
                u.user_name as "Пользователь",
                st.subscribe_type_name as "Тип подписки",
                st.subscribe_type_cost as "Стоимость",
                TO_CHAR(s.subscribe_start, 'DD.MM.YYYY') as "Дата начала",
                TO_CHAR(s.subscribe_finish, 'DD.MM.YYYY') as "Дата окончания"
            FROM subscribe s
            JOIN "User" u ON s.user_id = u.user_id
            JOIN subscribe_type st ON s.subscribe_type_id = st.subscribe_type_id
            {where_sql}
            ORDER BY s.subscribe_start DESC
            LIMIT :limit OFFSET :offset
        """)
        
        count_query = text(f"SELECT COUNT(*) FROM subscribe s {where_sql}")
        
        result = await self.session.execute(query, params)
        count_result = await self.session.execute(count_query, params)
        
        return result.mappings().all(), count_result.scalar()

    async def get_subscription_types(self):
        query = text("""
            SELECT 
                subscribe_type_id as value,
                subscribe_type_name as label,
                subscribe_type_cost as cost
            FROM subscribe_type 
            ORDER BY subscribe_type_id
        """)
        result = await self.session.execute(query)
        return result.mappings().all()