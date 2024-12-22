import logging
import warnings
from collections.abc import Awaitable, Callable

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.models import Response
from starlette.requests import Request

from app.routers.auth.auth_router import auth_router
from app.routers.health.health_router import health_router
from app.routers.images.images_router import images_router
from app.server.lifespan import lifespan

logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.CRITICAL)
logging.getLogger("meteostat").setLevel(logging.CRITICAL)
logging.getLogger("pandas").setLevel(logging.CRITICAL)
logging.getLogger("transformers").setLevel(logging.CRITICAL)
logging.getLogger("insightface").setLevel(logging.CRITICAL)
warnings.simplefilter(action="ignore", category=FutureWarning)
app = FastAPI(lifespan=lifespan)


@app.middleware("http")
async def log_exceptions(
        request: Request, call_next: Callable[[Request], Awaitable[Response]],
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
app.include_router(images_router)
app.include_router(health_router)
app.include_router(auth_router)


def main() -> None:
    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=9475,
        log_level="info",
        log_config="logging.yaml",
    )
