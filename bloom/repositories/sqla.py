"""SQLAlchemy-adapted repositories."""

from collections.abc import Hashable
from typing import Any, override

from sqlalchemy import delete, orm, select
from sqlalchemy.ext import asyncio

from bloom import domain
from bloom.repositories import abc


class SqlaRepository[T: domain.Entity[Any], E: Hashable](abc.BaseRepository[T, E]):
    """SQLAlchemy-adapted repository."""

    def __init__(self, entity_type: type[T], id_type: type[E], session: orm.Session):
        """Constructs a new repository."""
        super().__init__(entity_type, id_type)
        self._model = entity_type
        self._session = session

    @override
    def add(self, entity: T) -> None:
        self._session.add(entity)

    @override
    def get(self, entity_id: E) -> T | None:
        return self._session.scalar(
            select(self._model).where(self._model._id == entity_id)  # noqa: SLF001
        )

    @override
    def remove(self, entity_id: E) -> None:
        self._session.execute(delete(self._model).where(self._model._id == entity_id))  # noqa: SLF001

    @override
    def list(self) -> list[T]:
        return list(self._session.scalars(select(self._model)))


class AsyncSqlaRepository[T: domain.Entity[Any], E: Hashable](
    abc.BaseAsyncRepository[T, E]
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
    def add(self, entity: T) -> None:
        self._session.add(entity)

    @override
    async def get(self, entity_id: E) -> T | None:
        return await self._session.scalar(
            select(self._model).where(self._model._id == entity_id)  # noqa: SLF001
        )

    @override
    async def remove(self, entity_id: E) -> None:
        await self._session.execute(
            delete(self._model).where(self._model._id == entity_id)  # noqa: SLF001
        )

    @override
    async def list(self) -> list[T]:
        return list(await self._session.scalars(select(self._model)))
