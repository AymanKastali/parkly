from abc import ABC, abstractmethod


class IdGenerator[T](ABC):
    @abstractmethod
    def generate(self) -> T: ...
