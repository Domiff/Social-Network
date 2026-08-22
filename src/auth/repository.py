from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User
from src.core.database import BaseRepository


class UserRepository(BaseRepository):
    async def create(self, data: dict) -> User:
        query = insert(User).values(data).returning(User)
        result = await self.session.execute(query)
        await self.session.commit()
        return result.scalar_one()

    async def list(self) -> list[User]:
        query = select(User)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_email(self, email: str) -> User:
        query = select(User).where(User.email == email, User.is_active)
        result = await self.session.execute(query)
        return result.scalar_one()

    async def get_by_id(self, id_: int) -> User:
        query = select(User).where(User.id == id_, User.is_active)
        result = await self.session.execute(query)
        return result.scalar_one()

    async def delete(self, email: str, is_soft: bool) -> bool:
        if is_soft:
            query = update(User).where(User.email == email).values(is_active=False)
        else:
            query = delete(User).where(User.email == email)
        result = await self.session.execute(query)
        await self.session.commit()
        return bool(result.rowcount)

    async def update(self, email: str, data: dict) -> bool:
        query = update(User).where(User.email == email).values(data)
        result = await self.session.execute(query)
        await self.session.commit()
        return bool(result.rowcount)


def get_user_repo(session: AsyncSession) -> UserRepository:
    return UserRepository(session)
