from dishka import Provider, Scope

service_provider = Provider()


def service[T](cls: type[T]) -> type[T]:
    """Mark a class as a container-managed service (registered on import).

    To add a service: put @service on the class, then resolve it from the
    container where it's used (e.g. Nene._add_commands).
    An unregistered dependency fails loudly at startup (dishka graph check).
    """
    service_provider.provide(cls, scope=Scope.APP)
    return cls
