from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from models.user import User
from schemas.user import UserCreate, UserUpdate
from repositories.user_repository import UserRepository

class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def create_user(self, db: AsyncSession, user_data: UserCreate) -> User:
        if await self.repo.get_by_email(db, user_data.email):
            raise HTTPException(400, "Email already exists")
        user = User(name=user_data.name, email=user_data.email, hashed_password=user_data.hashed_password)
        return await self.repo.create(db, user)

    async def get_user(self, db: AsyncSession, user_id: int) -> User:
        user = await self.repo.get_by_id(db, user_id)
        if not user:
            raise HTTPException(404, "User not found")
        return user
    
    async def get_user(self, db: AsyncSession, user_email: str) -> User:
        user = await self.repo.get_by_email(db, user_email)
        if not user:
            raise HTTPException(404, "User not found")
        return user
    
    async def check_user(self, db: AsyncSession, email: str, hashed_password: str):
        user = await self.get_user(db, email)
        if user.hashed_password != hashed_password:
            raise HTTPException(400, "Invalid Credentials")

    async def update_user(self, db: AsyncSession, user_id: int, data: UserUpdate) -> User:
        user = await self.get_user(db, user_id)

        if data.email and data.email != user.email:
            if await self.repo.get_by_email(db, data.email):
                raise HTTPException(400, "Email already in use")

        if data.name:
            user.name = data.name
        if data.email:
            user.email = data.email
        if data.phone:
            user.phone = data.phone
        if data.gym_yoe:
            user.gym_yoe = data.gym_yoe
        if data.age:
            user.age = data.age
        if data.role:
            user.role = data.role
        

        return await self.repo.update(db, user)

    async def delete_user(self, db: AsyncSession, user_id: int):
        user = await self.get_user(db, user_id)
        await self.repo.delete(db, user)