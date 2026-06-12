from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.auth.router import router as auth_router
from src.core.config import settings
from src.core.database import ping_database
from src.core.logging import configure_logging, get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    params = {
        "is_debug": settings.app.IS_DEBUG,
        "is_dockerized": settings.app.IS_DOCKERIZED,
    }
    logger.info("Starting application", **params)
    logger.info("Application started")

    yield

    logger.info("Starting graceful shutdown")
    logger.info("Graceful shutdown completed")


def create_app() -> FastAPI:
    configure_logging()
    logger.info("Creating FastAPI application")

    app = FastAPI(
        title="Social Network",
        version="1",
        lifespan=lifespan,
        openapi_url="/openapi.json" if settings.app.IS_DEBUG else None,
    )

    setup_middlewares(app)
    setup_healthcheck(app)
    app.include_router(auth_router)

    logger.info("Application routes configured")

    return app


def setup_middlewares(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_credentials=settings.cors.ALLOW_CREDENTIALS,
        allow_origins=settings.cors.ALLOW_ORIGINS,
        allow_methods=settings.cors.ALLOW_METHODS,
    )
    logger.info(
        "CORS middleware configured", allowed_origins=settings.cors.ALLOW_ORIGINS
    )


def setup_healthcheck(app: FastAPI) -> None:
    @app.get("/health", tags=["Health"])
    async def health() -> bool:
        is_database_available = await ping_database()
        if not is_database_available:
            logger.warning("Healthcheck failed: database is unavailable")
        return is_database_available
