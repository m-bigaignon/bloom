"""SQLAlchemy-adapted repositories."""

from collections.abc import Hashable
from typing import Any, override

from sqlalchemy import orm, select
from sqlalchemy.ext import asyncio

from bloom import domain
from bloom.repositories import abc


class SqlaRepository[T: domain.Entity[Any], E: Hashable](abc.AbstractRepository[T, E]):
    """SQLAlchemy-adapted repository."""

    def __init__(self, entity_type: type[T], id_type: type[E], session: orm.Session):
        """Constructs a new repository."""
        super().__init__(entity_type, id_type)
        self._model = entity_type
        self._session = session

    @override
    def _add(self, entity: T) -> None:
        """Placeholder."""
        self._session.add(entity)

    @override
    def _get(self, entity_id: E) -> T | None:
        """Placeholder."""
        return self._session.scalar(
            select(self._model).where(self._model._id == entity_id)  # noqa: SLF001
        )

    def remove(self, entity_id: E) -> None:
        """Placeholder."""
        return

    @override
    def _all(self) -> list[T]:
        return list(self._session.scalars(select(self._model)))


class AsyncSqlaRepository[T: domain.Entity[Any], E: Hashable](
    abc.AsyncAbstractRepository[T, E]
):
    """SQLAlchemy-adapted repository."""

    def __init__(
        self, entity_type: type[T], id_type: type[E], session: asyncio.AsyncSession
    ):
        """Constructs a new repository."""
        super().__init__(entity_type, id_type)
        self._model = entity_type
        self._session = session

    @override
    def _add(self, entity: T) -> None:
        self._session.add(entity)

    @override
    async def _get(self, entity_id: E) -> T | None:
        return await self._session.scalar(
            select(self._model).where(self._model._id == entity_id)  # noqa: SLF001
        )

    async def remove(self, entity_id: E) -> None:
        """Placeholder."""
        return

    @override
    async def _all(self) -> list[T]:
        return list(await self._session.scalars(select(self._model)))
