from typing import Any

import sqlalchemy as sqla
from sqlalchemy import orm


def is_column[T: type](entry: orm.Mapper[T], attr: str) -> bool:
    return attr in entry.columns


def is_relation[T: type](entry: orm.Mapper[T], attr: str) -> bool:
    return attr in entry.relationships


def parse(entry: str):
    args = entry.split("__")
    return args


class QuerySet[T: type]:
    def __init__(self, model: T):
        self.stmt = sqla.select(model)
        self._mapper = sqla.inspect(model)

    def filter(self, **kwargs: Any) -> "QuerySet[T]":
        for entry in kwargs:
            infos = parse(entry)
            print(infos[0])
            print(is_column(self._mapper, infos[0]))
            print(is_relation(self._mapper, infos[0]))

        return self


class SQLARepo:
    def __init__(self, model: type):
        self.model = model

    def all(self):
        return QuerySet(self.model)
