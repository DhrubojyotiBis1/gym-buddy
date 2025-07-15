from schemas.authentication import SigninUser, SignupUser
from grpc_service.client.user_client_connector import UserClientConnector
from abc import ABC, abstractmethod


class IUserClient(ABC):
    @abstractmethod
    async def signin(self, connecter: UserClientConnector, user: SigninUser): pass

    @abstractmethod
    async def signup(self, connecter: UserClientConnector, user: SignupUser): pass
