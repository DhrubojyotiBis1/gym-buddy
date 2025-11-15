from fastapi import FastAPI
from routers import direct_chat_router
from exceptions.http_exception_handler import register_exception_handlers

app = FastAPI(
    title="Direct Chat Service",
    docs_url="/direct-chat/docs",
    redoc_url="/direct-chat/redoc",
    openapi_url="/direct-chat/openapi.json"
)
app.include_router(direct_chat_router.router)

register_exception_handlers(app)