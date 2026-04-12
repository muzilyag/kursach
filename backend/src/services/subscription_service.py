from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

class SubscriptionService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def change_subscription(self, user_id: int, new_subscribe_type_id: int, payment_method: str):
        query = text("""
            CALL change_subscription_type(
                p_user_id := :user_id,
                p_new_subscribe_type_id := :new_type_id,
                p_payment_method := :method
            )
        """)
        
        await self.session.execute(query, {
            "user_id": user_id,
            "new_type_id": new_subscribe_type_id,
            "method": payment_method
        })
        await self.session.commit()
        return True