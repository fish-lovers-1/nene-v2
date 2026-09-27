from collections.abc import AsyncIterator

import aiohttp
from dishka import Provider, Scope, provide


class HttpProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_session(self) -> AsyncIterator[aiohttp.ClientSession]:
        async with aiohttp.ClientSession() as session:
            yield session
