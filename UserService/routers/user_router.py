from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.user import UserCreate, UserUpdate, UserResponse
from services.user_service import UserService
from repositories.user_repository import UserRepository
from jwt_service.jwt_service import verify_jwt
from database import get_db

router = APIRouter(prefix="/users", tags=["Users"])
user_service = UserService(UserRepository())

'''@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    return await user_service.create_user(db, user)'''

#TODO: remove user_id use user_email
@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, user_email: str = Depends(verify_jwt), db: AsyncSession = Depends(get_db)):
    return await user_service.get_user(db, user_id)

#TODO: remove user_id use user_email
@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, data: UserUpdate, user_email: str = Depends(verify_jwt), db: AsyncSession = Depends(get_db)):
    return await user_service.update_user(db, user_id, data)

#TODO: remove user_id use user_email
@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: int, user_email: str = Depends(verify_jwt), db: AsyncSession = Depends(get_db)):
    await user_service.delete_user(db, user_id)
    return None
