from grpc_service.stubs.authentication import authentication_pb2_grpc
from config import Config
from grpc_service.server.service import UserAuthenticationService
from grpc import aio
import asyncio

async def serve():
    server = aio.server()
    authentication_pb2_grpc.add_UserAuthenticationServicer_to_server(UserAuthenticationService(), server=server)
    server.add_insecure_port(f"{Config.GRPC_IP}:{Config.GRPC_PORT}")
    await server.start()
    await server.wait_for_termination()


if __name__ == "__main__":
    asyncio.run(serve())