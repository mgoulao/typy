
from abc import ABC, abstractmethod


class Encodable(ABC):
    @abstractmethod
    def encode(self):
        pass
