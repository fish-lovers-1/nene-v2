from dataclasses import dataclass

from dishka import Provider, Scope, provide

from services.trivia_service import TriviaService


@dataclass
class Services:
    """Everything the bot needs, in one stable object.

    New services are one field here (+ one provide() line below).
    """

    trivia_service: TriviaService


class ServiceProvider(Provider):
    scope = Scope.APP

    # Auto-wired via __init__ hints. New services are one line here,
    # no new provider files needed.
    trivia_service = provide(TriviaService)
    services = provide(Services)
