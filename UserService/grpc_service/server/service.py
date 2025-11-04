import logging
import grpc
from grpc_service.stubs.authentication import authentication_pb2_grpc, authentication_pb2
from services.user_service import UserService
from schemas.user import UserCreate
from repositories.user_repository import UserRepository
from database import get_db
from grpc_service.exceptions.http_exception_handler import http_exception_handler

# Setup logging for the gRPC service
logger = logging.getLogger("grpc-service")
logger.setLevel(logging.INFO)

user_service = UserService(UserRepository())

class UserAuthenticationService(authentication_pb2_grpc.UserAuthenticationServicer):
    @http_exception_handler()
    async def signin(self, request, context):
        logger.info(f"Received signin request for email: {request.email}")
        gen = get_db()
        db = await gen.__anext__()
        try:
            await user_service.check_user(db, email=request.email, hashed_password=request.hashed_password)
            logger.info(f"User signin successful for email: {request.email}")
        except Exception as e:
            logger.error(f"Signin failed for email: {request.email}: {e}")
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            return authentication_pb2.Response(message="Signin failed: " + str(e))
        finally:
            await gen.aclose()
        response = authentication_pb2.Response(message="Login Successful")
        return response

    @http_exception_handler()
    async def signup(self, request, context):
        logger.info(f"Received signup request for email: {request.email}, name: {request.name}")
        gen = get_db()
        db = await gen.__anext__()
        try:
            user = UserCreate(name=request.name, email=request.email, hashed_password=request.hashed_password)
            await user_service.create_user(db, user_data=user)
            logger.info(f"User signup successful for email: {request.email}")
        except Exception as e:
            logger.error(f"Signup failed for email: {request.email}: {e}")
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            return authentication_pb2.Response(message="Signup failed: " + str(e))
        finally:
            await gen.aclose()
        response = authentication_pb2.Response(message="Signup Successful")
        return response