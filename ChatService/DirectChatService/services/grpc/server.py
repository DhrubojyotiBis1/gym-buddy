from services.grpc.stubs import chat_deliver_pb2_grpc
from config import Config
from services.grpc.service import MessageDeliveryService
from grpc import aio
import asyncio

async def serve():
    server = aio.server()
    chat_deliver_pb2_grpc.add_DirectChatServicer_to_server(MessageDeliveryService(), server=server)
    server.add_insecure_port(f"{Config.GRPC_IP}:{Config.GRPC_PORT}")
    await server.start()
    await server.wait_for_termination()

if __name__ == "__main__":
    asyncio.run(serve())