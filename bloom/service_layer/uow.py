"""Base classes for the unit of work pattern."""

import abc
from collections.abc import Generator
from contextlib import contextmanager
from typing import Self, override

from sqlalchemy import orm


class AbstractUnitOfWork(abc.ABC):
    """Base class for any Unit of Work."""

    @contextmanager
    def __call__(self) -> Generator[Self]:
        """Start the unit of work context manager."""
        try:
            yield self
            self.commit()
        except Exception:
            self.rollback()
            raise

    @abc.abstractmethod
    def commit(self) -> None:
        """Commits changes in this unit of work."""

    @abc.abstractmethod
    def rollback(self) -> None:
        """Rolls back the changes for this unit of work."""


class AbstractSqlaUnitOfWork(AbstractUnitOfWork, abc.ABC):
    """An abstract SQLAlchemy-adapted unit of work."""

    def __init__(self, session_factory: orm.sessionmaker[orm.Session]):
        """Create a new unit of work."""
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

    @override
    def commit(self) -> None:
        self._session.commit()

    @override
    def rollback(self) -> None:
        self._session.rollback()


class AbstractMemoryUnitOfWork(AbstractUnitOfWork, abc.ABC):
    """An abstract in-memory unit of work."""

    def __init__(self) -> None:
        """Create a new unit of work."""
        self.committed = False

    @override
    def commit(self) -> None:
        self.committed = True

    @override
    def rollback(self) -> None:
        pass
