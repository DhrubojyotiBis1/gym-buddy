from fastapi import FastAPI
from logger import setup_logging
from routers import direct_chat_router
from exceptions.websocket_exception_handler import register_exception_handlers
from database import Base, engine
from services.kafka.kafka_client import close_kafka_connection

#setup_logging()

app = FastAPI(
    title="Direct Chat Service",
    docs_url="/direct-chat/docs",
    redoc_url="/direct-chat/redoc",
    openapi_url="/direct-chat/openapi.json"
)
app.include_router(direct_chat_router.router)


@app.on_event("startup")
async def on_startup():
    #TODO: start grpc service

    #TODO: Remove in production add alembic
    # Creating table if not already present
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("shutdown")
async def shutdown_event():
    await close_kafka_connection()
 

register_exception_handlers(app)