"""Base classes for the unit of work pattern."""

import abc
from asyncio import current_task
from collections.abc import AsyncGenerator, Generator
from contextlib import asynccontextmanager, contextmanager
from typing import Any, Self, override

from sqlalchemy import orm
from sqlalchemy.ext import asyncio

from bloom import domain, events
from bloom.repositories import abc as repo_abc


class AbstractUnitOfWork(abc.ABC):
    """Base class for any Unit of Work."""

    def __init__(self, event_bus: events.HandlersRegistry | None = None) -> None:
        """Initialize the unit of work with optional event bus."""
        self._event_bus = event_bus
        self._repositories: list[
            repo_abc.TrackingRepository[domain.Entity[Any], Any]
        ] = []

    @override
    def __setattr__(self, name: str, value: Any) -> None:
        """Intercept repository assignments to track them."""
        super().__setattr__(name, value)
        if isinstance(value, repo_abc.TrackingRepository):
            if not hasattr(self, "_repositories"):
                super().__setattr__("_repositories", [])
            self._repositories.append(value)

    def collect_events(self) -> list[events.Event[Any]]:
        """Collect all events from tracked aggregates in all repositories.

        Returns:
            List of all domain events from tracked aggregates.
        """
        collected_events: list[events.Event[Any]] = []
        for repo in self._repositories:
            for entity in repo.tracked:
                if isinstance(entity, domain.Aggregate):
                    collected_events.extend(entity.flush_events())
        return collected_events

    def _publish_events(self, event_list: list[events.Event[Any]]) -> None:
        """Publish events to the event bus.

        Args:
            event_list: List of events to publish.
        """
        if self._event_bus:
            for event in event_list:
                self._event_bus.handle(event)

    @contextmanager
    def __call__(self) -> Generator[Self]:
        """Start the unit of work context manager."""
        try:
            yield self
        except Exception:
            self.rollback()
            raise
        else:
            collected_events = self.collect_events()
            if collected_events:
                self._publish_events(collected_events)

    @abc.abstractmethod
    def commit(self) -> None:
        """Commits changes in this unit of work."""

    @abc.abstractmethod
    def rollback(self) -> None:
        """Rolls back the changes for this unit of work."""


class AbstractSqlaUnitOfWork(AbstractUnitOfWork, abc.ABC):
    """An abstract SQLAlchemy-adapted unit of work."""

    def __init__(
        self,
        session_factory: orm.sessionmaker[orm.Session],
        event_bus: events.HandlersRegistry | None = None,
    ):
        """Create a new unit of work."""
        super().__init__(event_bus)
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

    def __init__(self, event_bus: events.HandlersRegistry | None = None) -> None:
        """Create a new unit of work."""
        super().__init__(event_bus)
        self.committed = False

    @override
    def commit(self) -> None:
        self.committed = True

    @override
    def rollback(self) -> None:
        pass


class AbstractAsyncUnitOfWork(abc.ABC):
    """Base class for any Unit of Work."""

    def __init__(self, event_bus: events.AsyncHandlersRegistry | None = None) -> None:
        """Initialize the unit of work with optional async event bus."""
        self._event_bus = event_bus
        self._repositories: list[
            repo_abc.AsyncTrackingRepository[domain.Entity[Any], Any]
        ] = []

    @override
    def __setattr__(self, name: str, value: Any) -> None:
        """Intercept repository assignments to track them."""
        super().__setattr__(name, value)
        if isinstance(value, repo_abc.AsyncTrackingRepository):
            if not hasattr(self, "_repositories"):
                super().__setattr__("_repositories", [])
            self._repositories.append(value)

    def collect_events(self) -> list[events.Event[Any]]:
        """Collect all events from tracked aggregates in all repositories.

        Returns:
            List of all domain events from tracked aggregates.
        """
        collected_events: list[events.Event[Any]] = []
        for repo in self._repositories:
            for entity in repo.tracked:
                if isinstance(entity, domain.Aggregate):
                    collected_events.extend(entity.flush_events())
        return collected_events

    async def _publish_events(self, event_list: list[events.Event[Any]]) -> None:
        """Publish events to the async event bus.

        Args:
            event_list: List of events to publish.
        """
        if self._event_bus:
            for event in event_list:
                await self._event_bus.handle(event)

    @asynccontextmanager
    async def __call__(self) -> AsyncGenerator[Self]:
        """Start the unit of work context manager."""
        try:
            yield self
        except Exception:
            await self.rollback()
            raise
        else:
            collected_events = self.collect_events()
            if collected_events:
                await self._publish_events(collected_events)

    @abc.abstractmethod
    async def commit(self) -> None:
        """Commits changes in this unit of work."""

    @abc.abstractmethod
    async def rollback(self) -> None:
        """Rolls back the changes for this unit of work."""


class AbstractAsyncSqlaUnitOfWork(AbstractAsyncUnitOfWork, abc.ABC):
    """An abstract SQLAlchemy-adapted unit of work."""

    def __init__(
        self,
        session_factory: asyncio.async_sessionmaker[asyncio.AsyncSession],
        event_bus: events.AsyncHandlersRegistry | None = None,
    ):
        """Create a new unit of work."""
        super().__init__(event_bus)
        self._session_factory = asyncio.async_scoped_session(
            session_factory, current_task
        )

    @override
    @asynccontextmanager
    async def __call__(self) -> AsyncGenerator[Self]:
        self._session = self._session_factory()
        async with super().__call__() as uow:
            try:
                yield uow
            finally:
                await self._session_factory.remove()

    @override
    async def commit(self) -> None:
        await self._session.commit()

    @override
    async def rollback(self) -> None:
        await self._session.rollback()


class AbstractAsyncMemoryUnitOfWork(AbstractAsyncUnitOfWork, abc.ABC):
    """An abstract in-memory unit of work."""

    def __init__(self, event_bus: events.AsyncHandlersRegistry | None = None) -> None:
        """Create a new unit of work."""
        super().__init__(event_bus)
        self.committed = False

    @override
    async def commit(self) -> None:
        self.committed = True

    @override
    async def rollback(self) -> None:
        pass
