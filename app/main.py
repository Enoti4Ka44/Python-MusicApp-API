from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import engine, Base
import app.models
from app.routes import routers



@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield


app = FastAPI(lifespan=lifespan)

for router in routers:
    app.include_router(router)
