from grpc_service.stubs.authentication import authentication_pb2_grpc, authentication_pb2
from services.user_service import UserService
from schemas.user import UserCreate
from repositories.user_repository import UserRepository
from database import get_db
from grpc_service.exceptions.http_exception_handler import http_exception_handler

user_service = UserService(UserRepository())

class UserAuthenticationService(authentication_pb2_grpc.UserAuthenticationServicer):
    @http_exception_handler()
    async def signin(self, request, context):
        gen = get_db()
        db = await gen.__anext__()
        try:
            await user_service.check_user(db, email=request.email, hashed_password=request.hashed_password)
        finally:
            await gen.aclose()
        response = authentication_pb2.Response(message="Login Successful")
        return response
    
    @http_exception_handler()
    async def signup(self, request, context):
        print("yesss")
        gen = get_db()
        db = await gen.__anext__()
        try:
            user = UserCreate(name=request.name, email=request.email, hashed_password=request.hashed_password)
            await user_service.create_user(db, user_data=user)
        finally:
            await gen.aclose()
        response = authentication_pb2.Response(message="Signup Successful")
        return response