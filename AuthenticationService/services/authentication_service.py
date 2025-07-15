from schemas.authentication import SigninUser, SignupUser, Auth
from grpc_service.client.user_client_connector import UserClientConnector
from grpc_service.client.user_client_interface import IUserClient
from jwt_service.service import JWT

class AuthenticationService:
    def __init__(self, user_client: IUserClient):
        self.user_client = user_client
        self.jwt = JWT()

    def _create_auth_from_token(self, tokens: dict) -> Auth:
        return Auth(access=tokens['access_token'], refres=tokens['refresh_token'])

    async def signup_user(self, connector: UserClientConnector, user: SignupUser):
        await self.user_client.signup(connector, user)
        return self._create_auth_from_token(self.jwt.create_new_tokens(user.email))

    async def signin_user(self, connector: UserClientConnector, user: SigninUser):
        await self.user_client.signin(connector, user)
        return self._create_auth_from_token(self.jwt.create_new_tokens(user.email))

    async def refresh_token(self, refresh_token: str):
        return self._create_auth_from_token(self.jwt.refresh_token(refresh_token))
