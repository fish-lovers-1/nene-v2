from collections.abc import AsyncIterator

from dishka import Provider, Scope, alias, provide

from config import EnvConfig
from db.Database import Database, SessionFactory


class DbProvider(Provider):
    session_factory = alias(source=Database, provides=SessionFactory)

    @provide(scope=Scope.APP)
    async def get_db(self, env: EnvConfig) -> AsyncIterator[Database]:
        db = Database(env.DATABASE_URL)
        await db.init()
        yield db
        await db.close()
