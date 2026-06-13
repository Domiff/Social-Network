from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User
from src.core.database import BaseRepository
from src.core.exceptions import AlreadyExists, DoesNotExists
from src.core.logging import get_logger

logger = get_logger(__name__)


class UserRepository(BaseRepository):
    async def create(self, data: dict) -> User:
        try:
            query = insert(User).values(data).returning(User)
            result = await self.session.execute(query)
            await self.session.commit()
            logger.info("User created successfully")
            return result.scalar_one()
        except IntegrityError as e:
            await self.session.rollback()
            logger.error("User already exists")
            raise AlreadyExists() from e

    async def list(self) -> list[User]:
        query = select(User)
        result = await self.session.execute(query)
        users = result.scalars().all()
        if not users:
            raise DoesNotExists()
        return users

    async def get_by_email(self, email: str) -> User:
        try:
            query = select(User).where(User.email == email, User.is_active)
            result = await self.session.execute(query)
            return result.scalar_one()
        except NoResultFound as e:
            logger.error("User does not exist")
            raise DoesNotExists() from e

    async def get_by_id(self, id_: int) -> User:
        try:
            query = select(User).where(User.id == id_, User.is_active)
            result = await self.session.execute(query)
            return result.scalar_one()
        except NoResultFound as e:
            logger.error("User does not exist")
            raise DoesNotExists() from e

    async def delete(self, email: str, is_soft: bool) -> bool:
        try:
            if is_soft:
                query = update(User).where(User.email == email).values(is_active=False)
            else:
                query = delete(User).where(User.email == email)
            await self.session.execute(query)
            await self.session.commit()
            logger.info("User deleted")
            return True
        except NoResultFound as e:
            logger.error("User does not exist")
            raise DoesNotExists() from e

    async def update(self, email: str, data: dict) -> bool:
        try:
            session = update(User).where(User.email == email).values(data)
            await self.session.execute(session)
            await self.session.commit()
            logger.info("User updated")
            return True
        except NoResultFound as e:
            logger.error("User does not exist")
            raise DoesNotExists() from e


def get_user_repo(session: AsyncSession) -> UserRepository:
    return UserRepository(session)
