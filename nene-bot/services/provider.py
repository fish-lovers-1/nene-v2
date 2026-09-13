from dishka import Provider, Scope, provide

from services.trivia_service import TriviaService


class ServiceProvider(Provider):
    scope = Scope.APP

    # Auto-wired via __init__ hints. New services are one line here,
    # no new provider files needed.
    trivia_service = provide(TriviaService)
