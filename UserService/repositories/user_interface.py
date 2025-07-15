from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from models.user import User
from models.enums import UserRole

class IUserRepository(ABC):

    @abstractmethod
    def create(self, db: AsyncSession, user: User) -> User: pass

    @abstractmethod
    def get_by_id(self, db: AsyncSession, user_id: int) -> User | None: pass

    @abstractmethod
    def get_by_email(self, db: AsyncSession, email: str) -> User | None: pass

    @abstractmethod
    def get_by_phone(self, db: AsyncSession, phone: str) -> User | None: pass

    @abstractmethod
    def get_by_role(self, db: AsyncSession, role: UserRole) -> User | None: pass

    @abstractmethod
    def update(self, db: AsyncSession, user: User) -> User: pass

    @abstractmethod
    def delete(self, db: AsyncSession, user: User) -> None: pass
