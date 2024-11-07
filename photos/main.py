import logging
from collections.abc import Callable, Awaitable

from fastapi import FastAPI
from fastapi.openapi.models import Response
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request

from photos.server.lifespan import lifespan
from photos.server.routers.auth.auth_router import auth_router
from photos.server.routers.health.health_router import health_router
from photos.server.routers.images.images_router import images_router

logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.DEBUG)
app = FastAPI(lifespan=lifespan)


@app.middleware("http")
async def log_exceptions(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    try:
        return await call_next(request)
    except Exception as e:
        logging.exception("Unhandled exception occurred")
        raise e


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

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=9475,
        log_level="info",
        log_config="logging.yaml",
    )
