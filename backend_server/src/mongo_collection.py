import yaml

from typing import Any, Iterable

from icollection import ICollection


class MongoCollection(ICollection):
    def __init__(self, url: str, db: str, collection: str):
        from pymongo import MongoClient
        client = MongoClient(url)
        self.__collection = client[db][collection]

    def insert_one(self, item: dict) -> None:
        self.__collection.insert_one(item)

    def set_one(self, id: int, field: str, value: Any) -> None:
        self.__collection.update_one({'_id': id}, {'$set': {field: value}})

    def push_to_one(self, id: int, field: str, value: Any) -> None:
        self.__collection.update_one({'_id': id}, {'$push': {field: value}})

    def find_one(self, filter: dict) -> dict:
        self.__collection.find_one(filter)

    def find_many(self, filter: dict) -> Iterable[dict]:
        for item in self.__collection.find(filter):
            yield item
