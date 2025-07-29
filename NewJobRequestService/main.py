from fastapi import FastAPI
from routers import new_job_request_router
from exceptions.http_exception_handler import register_exception_handlers

app = FastAPI()
app.include_router(new_job_request_router.router)

register_exception_handlers(app)