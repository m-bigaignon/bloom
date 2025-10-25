"""In-memory repository."""

from collections.abc import Hashable
from typing import Any, override

from bloom import domain
from bloom.repositories import abc


class InMemoryRepository[T: domain.Entity[Any], E: Hashable](
    abc.AbstractRepository[T, E]
):
    """In-memory repository implementation for testing and prototyping.

    Stores entities in a dictionary keyed by their ID.
    Not suitable for production use, but ideal for unit tests and rapid prototyping.

    Type Parameters:
        T: The entity type this repository manages
        E: The id type of the entity type
    """

    def __init__(self, entity_type: type[T], id_type: type[E]):
        """Initialize an empty in-memory repository."""
        super().__init__(entity_type, id_type)
        self._entities: dict[E, T] = {}

    @override
    def _get(self, entity_id: E) -> T | None:
        return self._entities.get(entity_id)

    @override
    def _add(self, entity: T) -> None:
        self._entities[entity.id] = entity

    @override
    def _all(self) -> list[T]:
        return list(self._entities.values())

    def remove(self, entity_id: E) -> None:
        """Placeholder."""
        return


class AsyncInMemoryRepository[T: domain.Entity[Any], E: Hashable](
    abc.AsyncAbstractRepository[T, E]
):
    """In-memory repository implementation for testing and prototyping.

    Stores entities in a dictionary keyed by their ID.
    Not suitable for production use, but ideal for unit tests and rapid prototyping.

    Type Parameters:
        T: The entity type this repository manages
        E: The id type of the entity type
    """

    def __init__(self, entity_type: type[T], id_type: type[E]):
        """Initialize an empty in-memory repository."""
        super().__init__(entity_type, id_type)
        self._entities: dict[E, T] = {}

    @override
    def _add(self, entity: T) -> None:
        self._entities[entity.id] = entity

    @override
    async def _get(self, entity_id: E) -> T | None:
        return self._entities.get(entity_id)

    @override
    async def _all(self) -> list[T]:
        return list(self._entities.values())

    async def remove(self, entity_id: E) -> None:
        """Placeholder."""
        return
