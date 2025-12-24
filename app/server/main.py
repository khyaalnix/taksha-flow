import os
import asyncio
from contextlib import asynccontextmanager
from math import ceil
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi_limiter import FastAPILimiter

from app import app_state
from app.utils.logger import LoggerFactory
from app.connectors.connectors import get_mongo_client, get_redis_client

logger = LoggerFactory().get_logger()

async def ratelimit_callback(
    request: Request, response: Response, pexpire: int
):
    expire = ceil(pexpire / 1000)
    raise HTTPException(
        status_code=429,
        detail=f"Rate limit exceeded. Retry after {expire} seconds.",
        headers={"Retry-After": str(expire)},
    )

@asynccontextmanager
async def lifespan(app_: FastAPI):
    try:
        app_state.resources["mongo"] = get_mongo_client()
        app_state.resources["redis"] = get_redis_client()
        await FastAPILimiter.init(
            redis=app_state.resources["redis"],
            http_callback=ratelimit_callback,
        )
        app_.state.app_state = app_state

        logger.info("Flow App Initialized 🚀")
        yield
    except Exception as e:
        logger.error("Flow App Initialization Failed ❌")
        raise e
    finally: 
        await app_state.resources["redis"].close()
        logger.info("Flow App Redis Connection Closed 🔌")  


app = FastAPI(
    title="Taksha Flow API",
    version="1.0",
    root_path="/flow",
    lifespan=lifespan,
)

# Parse WHITELISTED_ORIGINS from comma-separated string to list
whitelisted_origins = os.getenv("WHITELISTED_ORIGINS", "")
origins_list = [origin.strip() for origin in whitelisted_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Set-Cookie"]
)
# Add GZip compression for responses > 500 bytes
app.add_middleware(GZipMiddleware, minimum_size=500)

# include routers here...
from app.api.login import router as auth_router
app.include_router(auth_router) 


@app.get("/")
async def root():
    return {"message": "Taksha Flow API", "docs": "/flow/docs"}

@app.get("/health")
async def health():
    task1 = app_state.resources["redis"].ping()
    task2 = app_state.resources["mongo"].admin.command("ping")

    results = await asyncio.gather(task1, task2, return_exceptions=True)
    
    if all(results):
        return {"status": "healthy"}
    else:
        return {"status": "unhealthy"}
    



        