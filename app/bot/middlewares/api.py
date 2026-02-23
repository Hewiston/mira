from typing import Any, Awaitable, Callable, Dict
from aiogram.dispatcher.middlewares.base import BaseMiddleware

class ApiMiddleware(BaseMiddleware):
    def __init__(self, api_client):
        self.api_client = api_client

    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: Dict[str, Any],
    ) -> Any:
        data["api"] = self.api_client
        return await handler(event, data)