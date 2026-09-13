from dishka import Provider, Scope

service_provider = Provider()


def service[T](cls: type[T]) -> type[T]:
    """Mark a class as a container-managed service (registered on import).

    To add a service: put @service on the class, then add a field for it
    on Services in services/provider.py so Nene can reach it.
    Forgetting either step fails loudly at startup (dishka graph check).
    """
    service_provider.provide(cls, scope=Scope.APP)
    return cls
