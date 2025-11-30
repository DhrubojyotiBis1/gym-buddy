import asyncio

from fastapi import FastAPI
from routers import direct_chat_router
from exceptions.websocket_exception_handler import register_exception_handlers
from database import Base, engine
from services.kafka.kafka_client import close_kafka_connection
from services.grpc.server import serve as grpc_server

def create_app() -> FastAPI:
    app = FastAPI(
        title="Direct Chat Service",
        docs_url="/direct-chat/docs",
        redoc_url="/direct-chat/redoc",
        openapi_url="/direct-chat/openapi.json"
    )
    app.include_router(direct_chat_router.router)
    register_exception_handlers(app)

    @app.on_event("startup")
    async def on_startup():
        asyncio.get_running_loop().create_task(grpc_server())

        # NOTE: This is for dev/testing purposes. In production, use Alembic for migrations.
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @app.on_event("shutdown")
    async def on_shutdown():
        await close_kafka_connection()

    return app

app = create_app()