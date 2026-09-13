from dishka import Provider, Scope

client_provider = Provider()


def client[T](cls: type[T]) -> type[T]:
    """Mark a class as a container-managed API client (registered on import).

    Importing the module is what triggers registration — services that
    depend on the client already import its types, otherwise Dishka's
    graph check fails loudly at startup if no factory is found.
    """
    client_provider.provide(cls, scope=Scope.APP)
    return cls
