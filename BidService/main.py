from fastapi import FastAPI
from routers import bid_router
from exceptions.http_exception_handler import register_exception_handlers

app = FastAPI(
    title="Bid Service",
    docs_url="/bid/docs",
    redoc_url="/bid/redoc",
    openapi_url="/bid/openapi.json"
)
app.include_router(bid_router.router)

register_exception_handlers(app)