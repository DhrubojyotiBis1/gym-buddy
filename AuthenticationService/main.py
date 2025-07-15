from routers.authentication_router import router
from fastapi import FastAPI
from exceptions.handlers import register_exception_handlers

app = FastAPI()

register_exception_handlers(app)

app.include_router(router)