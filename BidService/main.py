from fastapi import FastAPI
from routers import bid_router
from exceptions.http_exception_handler import register_exception_handlers

app = FastAPI()
app.include_router(bid_router.router)

register_exception_handlers(app)