from routers.authentication_router import router
from fastapi import FastAPI
from exceptions.handlers import register_exception_handlers
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Authentication Service",
    docs_url="/authentication/docs",
    redoc_url="/authentication/redoc",
    openapi_url="/authentication/openapi.json"
)

register_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],        
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(router)