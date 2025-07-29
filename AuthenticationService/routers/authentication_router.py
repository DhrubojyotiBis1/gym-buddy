from fastapi import APIRouter, Depends
from schemas.authentication import Auth, SigninUser, SignupUser
from services.authentication_service import AuthenticationService
from grpc_service.client.user_client import UserClient
from grpc_service.client.user_client_connector import get_user_service_client_connoctor

import grpc
from starlette.exceptions import HTTPException as StarletteHTTPException

router = APIRouter(prefix="/authentication", tags=["Authentication"])
service = AuthenticationService(UserClient())

@router.post("/signup", response_model=Auth)
async def signup(signup_user: SignupUser, connector=Depends(get_user_service_client_connoctor)):
    try:
        result = await service.signup_user(connector, signup_user)
        return result
    except grpc.aio.AioRpcError as e:
        print(e.code(), e.details())
        raise StarletteHTTPException(400, 'User Exist')

@router.post("/signin", response_model=Auth)
async def signin(signin_user: SigninUser, connector=Depends(get_user_service_client_connoctor)):
    try:
        result = await service.signin_user(connector, signin_user)
        return result
    except grpc.aio.AioRpcError:
        raise StarletteHTTPException(404, 'Not Found')

@router.get("/refresh/{refresh_token}", response_model=Auth)
async def refresh(refresh_token: str):
    result = await service.refresh_token(refresh_token)
    return result