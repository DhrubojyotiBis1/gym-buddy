from fastapi import FastAPI
from routers import user_router
from database import Base, engine
from exceptions.handlers import register_exception_handlers

app = FastAPI(
    title="User Service",
    docs_url="/user/docs",
    redoc_url="/user/redoc",
    openapi_url="/user/openapi.json"
)

register_exception_handlers(app)

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(user_router.router)