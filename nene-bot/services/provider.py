from dataclasses import dataclass

from dishka import Scope

from services.registry import service_provider
from services.trivia_service import TriviaService


@dataclass
class Services:
    """Everything the bot needs, in one stable object.

    To add a service: put @service on the class, then add a field here.
    """

    trivia_service: TriviaService


service_provider.provide(Services, scope=Scope.APP)
