import abc
from collections.abc import Generator
from contextlib import contextmanager
from typing import Self, override

from sqlalchemy import orm


class AbstractUnitOfWork(abc.ABC):
    @contextmanager
    def __call__(self) -> Generator[Self]:
        try:
            yield self
            self.commit()
        except Exception:
            self.rollback()
            raise

    @abc.abstractmethod
    def commit(self): ...

    @abc.abstractmethod
    def rollback(self): ...


class AbstractSqlaUnitOfWork(AbstractUnitOfWork, abc.ABC):
    def __init__(self, session_factory: orm.sessionmaker):
        self._session_factory = orm.scoped_session(session_factory)

    @override
    @contextmanager
    def __call__(self) -> Generator[Self]:
        self._session = self._session_factory()
        with super().__call__() as uow:
            try:
                yield uow
            finally:
                self._session_factory.remove()

    def commit(self) -> None:
        self._session.commit()

    def rollback(self) -> None:
        self._session.rollback()


class AbstractMemoryUnitOfWork(AbstractUnitOfWork, abc.ABC):
    def __init__(self):
        self.committed = False

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        pass
