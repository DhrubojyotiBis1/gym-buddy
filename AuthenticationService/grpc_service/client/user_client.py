from grpc_service.client.user_client_interface import IUserClient
from grpc_service.stubs.userauthentication import userauthentication_pb2
from schemas.authentication import SigninUser, SignupUser
from grpc_service.client.user_client_connector import UserClientConnector

class UserClient(IUserClient):    
    async def signin(self, connector: UserClientConnector, user: SigninUser):
        request = userauthentication_pb2.UserCheck(email=user.email, hashed_password=user.hashed_password)
        response = await connector.stub.signin(request)
        return response
    
    async def signup(self, connector: UserClientConnector, user: SignupUser):
        request = userauthentication_pb2.UserCreate(name=user.name, email=user.email, hashed_password=user.hashed_password)
        response = await connector.stub.signup(request)
        return response