from grpc_service.stubs.userauthentication import userauthentication_pb2_grpc
from config import Config
from grpc_service.exceptions.unary_exception_handler import HttpExceptionHandlingInterceptor
from typing import Optional
from contextlib import asynccontextmanager
import grpc

class UserClientConnector():
    def __init__(self, interceptors: list = [], host: str = Config.USER_GRPC_CLIENT_HOST, port: int = Config.USER_GRPC_CLIENT_PORT):
        self.target = f"{host}:{port}"
        self.interceptors = interceptors
        self.channel: Optional[grpc.aio.Channel] = None
        self.stub: Optional[userauthentication_pb2_grpc.UserAuthenticationStub] = None

    async def connect(self):
        self.channel = grpc.aio.insecure_channel(self.target, interceptors=self.interceptors)
        self.stub = userauthentication_pb2_grpc.UserAuthenticationStub(self.channel)
    
    async def close(self):
        if self.channel:
            await self.channel.close()


@asynccontextmanager
async def user_service_client_connector_manager():
    client = UserClientConnector(interceptors=[HttpExceptionHandlingInterceptor()])
    await client.connect()
    try:
        yield client
    finally:
        await client.close()


async def get_user_service_client_connoctor():
    async with user_service_client_connector_manager() as connector:
        yield connector