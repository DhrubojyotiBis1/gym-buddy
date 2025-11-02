from fastapi import FastAPI
from routers import bid_notifier_router
from exceptions.http_exception_handler import register_exception_handlers

app = FastAPI(
    title="Bid-Notifier Service",
    docs_url="/bid-notifier/docs",
    redoc_url="/bid-notifier/redoc",
    openapi_url="/bid-notifier/openapi.json"
)
app.include_router(bid_notifier_router.router)

register_exception_handlers(app)