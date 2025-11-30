from services.direct_chat_gprc.stubs import chat_deliver_pb2_grpc
from typing import Optional
import grpc

class DirectChatClientConnector():
    def __init__(self, port: str, host: str, interceptors: list = []):
        self.target = f"{host}:{port}"
        self.interceptors = interceptors
        self.channel: Optional[grpc.aio.Channel] = None
        self.stub: Optional[chat_deliver_pb2_grpc.DirectChatStub] = None

    async def connect(self):
        self.channel = grpc.aio.insecure_channel(self.target, interceptors=self.interceptors)
        self.stub = chat_deliver_pb2_grpc.DirectChatStub(self.channel)
    
    async def close(self):
        if self.channel:
            await self.channel.close()