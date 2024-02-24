from abc import ABC, abstractmethod


class State(ABC):
    @abstractmethod
    def handle(self, *args, **kwargs):
        raise NotImplementedError
