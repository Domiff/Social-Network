import httpx

from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)


class HttpClientManager:
    def __init__(
        self,
        timeout: float,
        connect: float,
        max_connections: int,
        max_keepalive_connections: int,
        keepalive_expiry: float,
    ) -> None:
        self.default_timeout = httpx.Timeout(timeout, connect=connect)
        self.client_limits = httpx.Limits(
            max_connections=max_connections,
            max_keepalive_connections=max_keepalive_connections,
            keepalive_expiry=keepalive_expiry,
        )
        self.http_client: httpx.AsyncClient | None = None

    def _build_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            timeout=self.default_timeout,
            limits=self.client_limits,
            verify=settings.http.VERIFY,
        )

    async def startup(self) -> None:
        if self.http_client is not None:
            return
        self.http_client = self._build_client()
        logger.info("http_client started")

    async def shutdown(self) -> None:
        if self.http_client is not None:
            await self.http_client.aclose()
            self.http_client = None
        logger.info("http_client stopped")

    def get_client(self) -> httpx.AsyncClient:
        client = self.http_client
        if client is None:
            raise RuntimeError("HTTP client is not initialized")
        return client


http_client_manager = HttpClientManager(
    timeout=settings.http.TIMEOUT,
    connect=settings.http.CONNECT,
    max_connections=settings.http.MAX_CONNECTIONS,
    max_keepalive_connections=settings.http.MAX_KEEPALIVE_CONNECTIONS,
    keepalive_expiry=settings.http.KEEPALIVE_EXPIRY,
)
