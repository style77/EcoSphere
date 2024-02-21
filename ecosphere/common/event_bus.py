from ecosphere.common.singleton import SingletonMeta


class EventBus(metaclass=SingletonMeta):
    def __init__(self):
        self.listeners = {}

    def emit(self, event: str, *args, **kwargs):
        if event in self.listeners:
            for listener in self.listeners[event]:
                listener(*args, **kwargs)

    def listener(self, event: str):
        def decorator(func):
            if event not in self.listeners:
                self.listeners[event] = []
            self.listeners[event].append(func)
            return func

        return decorator

    def remove_listener(self, event: str, func):
        if event in self.listeners:
            self.listeners[event].remove(func)
        else:
            raise ValueError(f"Event {event} has no listeners.")


bus = EventBus()
