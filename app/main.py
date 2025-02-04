import logging
import warnings
from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.models import Response
from starlette.requests import Request

from app.routers.health.health_router import health_router
from app.routers.process.process_router import process_router
from app.routers.thumbnails.thumbnails_router import thumbnails_router

logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.CRITICAL)
logging.getLogger("meteostat").setLevel(logging.CRITICAL)
logging.getLogger("pandas").setLevel(logging.CRITICAL)
logging.getLogger("transformers").setLevel(logging.CRITICAL)
logging.getLogger("insightface").setLevel(logging.CRITICAL)
warnings.simplefilter(action="ignore", category=FutureWarning)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    print("Starting FastAPI server!")
    yield
    print("Closing FastAPI server :(")


app = FastAPI(lifespan=lifespan)


@app.middleware("http")
async def log_exceptions(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    try:
        return await call_next(request)
    except Exception:
        logging.exception("Unhandled exception occurred during call to endpoint.")
        raise


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(health_router)
app.include_router(thumbnails_router)
app.include_router(process_router)


def main() -> None:
    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=9475,
        log_level="info",
        log_config="logging.yaml",
    )
