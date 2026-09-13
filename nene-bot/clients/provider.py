from collections.abc import AsyncIterator

import aiohttp
from dishka import Provider, Scope, provide

from clients.opentdb import OpenTDBClient


class HttpProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_session(self) -> AsyncIterator[aiohttp.ClientSession]:
        async with aiohttp.ClientSession() as session:
            yield session


class ClientProvider(Provider):
    scope = Scope.APP

    # Auto-wired via __init__ hints. New API clients are one line here.
    opentdb_client = provide(OpenTDBClient)
