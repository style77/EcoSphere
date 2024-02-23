from typing import Any, Callable

from ecosphere.common.singleton import SingletonMeta


class AlreadyCalledError(Exception):
    pass


class OneTimeCaller(metaclass=SingletonMeta):
    def __init__(self, func: Callable):
        self.func = func
        self.called = False

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        if not self.called:
            self.called = True
            return self.func(*args, **kwds)
        raise AlreadyCalledError("This function can only be called once")
