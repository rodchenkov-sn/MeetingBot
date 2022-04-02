from typing import Any, Iterable
from collections.abc import Iterable

from icollection import ICollection

class MockCollection(ICollection):
    def __init__(self):
        self.items = []

    def insert_one(self, item: dict) -> None:
        self.items.append(item)

    def set_one(self, id: int, field: str, value: Any) -> None:
        for item in self.items:
            if item['_id'] == id:
                item[field] = value
                return
        raise ValueError('Item not found')
    
    def push_to_one(self, id: int, field: str, value: Any) -> None:
        for item in self.items:
            if item['_id'] == id:
                item[field].append(value)
                return
        raise ValueError('Item not found')

    def find_one(self, filter: dict) -> dict:
        for item in self.items:
            for k, v in filter.items():
                if isinstance(item[k], Iterable) and v not in item[k] or item[k] != v:
                    continue
                return item
        raise ValueError('Item not found')

    def find_many(self, filter: dict) -> Iterable[dict]:
        for item in self.items:
            found = True
            for k, v in filter.items():
                if isinstance(item[k], Iterable) and v in item[k]:
                    continue
                if item[k] != v:
                    found = False
            if found:
                yield item
