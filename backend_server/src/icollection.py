from abc import ABC, abstractmethod
from typing import Any, Iterable


class ICollection(ABC):
    @abstractmethod
    def insert_one(self, item: dict) -> None:
        pass

    @abstractmethod
    def set_one(self, id: int, field: str, value: Any) -> None:
        pass

    @abstractmethod
    def push_to_one(self, id: int, field: str, value: Any) -> None:
        pass

    @abstractmethod
    def find_one(self, filter: dict) -> dict:
        pass

    @abstractmethod
    def find_many(self, filter: dict) -> Iterable[dict]:
        pass
    