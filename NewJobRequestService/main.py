from fastapi import FastAPI
from routers import new_job_request_router
from exceptions.http_exception_handler import register_exception_handlers
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="New Job Request Service",
    docs_url="/new-job-request/docs",
    redoc_url="/new-job-request/redoc",
    openapi_url="/new-job-request/openapi.json"
)
app.include_router(new_job_request_router.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],        
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

register_exception_handlers(app)