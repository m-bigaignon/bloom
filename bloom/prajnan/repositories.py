"""Repository patterns and implementations for DDD."""

import abc
from collections.abc import Hashable
from types import get_original_bases
from typing import Any, Protocol, get_args, get_origin, override

from sqlalchemy import delete, orm, select

from bloom.sara import Entity


class Repository[T: Entity[Any], E: Hashable](Protocol):
    """Base abstract class defining the repository interface for entities.

    Repositories provide an abstraction over data persistence,
    allowing domain logic to remain independent of infrastructure concerns.

    Type Parameters:
        T: The entity type this repository manages (must have id: EntityIdT)
    """

    @abc.abstractmethod
    def add(self, entity: T) -> None:
        """Add a new entity to the repository.

        Args:
            entity: The entity to add.
        """

    @abc.abstractmethod
    def get(self, entity_id: E) -> T | None:
        """Retrieve an entity by its ID.

        Args:
            entity_id: The unique identifier of the entity.

        Returns:
            The entity if found, None otherwise.
        """

    @abc.abstractmethod
    def remove(self, entity_id: E) -> None:
        """Remove an entity from the repository.

        Args:
            entity_id: The unique identifier of the entity to remove.
        """

    @abc.abstractmethod
    def list(self) -> list[T]:
        """List all entities in the repository.

        Returns:
            A list of all entities.
        """


class BaseRepository[T: Entity[Any], E: Hashable](Repository[T, E]):
    def __init__(self, entity_type: type[T], id_type: type[E]):
        BaseRepository._validate_types(entity_type, id_type)

    @classmethod
    def _validate_types(cls, entity_type: type[T], id_type: type[E]) -> None:
        if get_origin(entity_type) is Entity:
            base = entity_type
            args = get_args(base)
            if len(args) == 0 or args[0] is not id_type:
                msg = "A1"
                raise TypeError(msg)
        else:
            type_ = (
                get_origin(entity_type)
                if get_origin(entity_type) is not None
                else entity_type
            )
            bases = get_original_bases(type_)
            for base in bases:
                cls._validate_types(base, id_type)


class InMemoryRepository[T: Entity[Any], E: Hashable](BaseRepository[T, E]):
    """In-memory repository implementation for testing and prototyping.

    Stores entities in a dictionary keyed by their ID.
    Not suitable for production use, but ideal for unit tests and rapid prototyping.

    Type Parameters:
        T: The entity type this repository manages
        E: The id type of the entity type

    Example:
        >>> class Product(Entity[int]):
        ...     pass
        >>> repo = InMemoryRepository(Product, int)
        >>> product = Product(123)
        >>> repo.add(product)
        >>> found = repo.get(123)

        >>> repo = InMemoryRepository(Product, str)  # ✗ Error: Product.id is int, not str
    """

    def __init__(self, entity_type: type[T], id_type: type[E]):
        """Initialize an empty in-memory repository."""
        super().__init__(entity_type, id_type)
        self._entities: dict[E, T] = {}

    @override
    def add(self, entity: T) -> None:
        """Add a new entity to the in-memory store."""
        self._entities[entity.id] = entity

    @override
    def get(self, entity_id: E) -> T | None:
        """Retrieve an entity by its ID from the in-memory store."""
        return self._entities.get(entity_id)

    @override
    def remove(self, entity_id: E) -> None:
        """Remove an entity from the in-memory store."""
        self._entities.pop(entity_id, None)

    @override
    def list(self) -> list[T]:
        """List all entities in the in-memory store."""
        return list(self._entities.values())


class SqlaRepository[T: Entity[Any], E: Hashable](BaseRepository[T, E]):
    def __init__(self, entity_type: type[T], id_type: type[E], session: orm.Session):
        super().__init__(entity_type, id_type)
        self._model = entity_type
        self._session = session

    @override
    def add(self, entity: T) -> None:
        self._session.add(entity)

    @override
    def get(self, entity_id: E) -> T | None:
        return self._session.scalar(
            select(self._model).where(self._model.id == entity_id)
        )

    @override
    def remove(self, entity_id: E) -> None:
        self._session.execute(delete(self._model).where(self._model.id == entity_id))

    @override
    def list(self) -> list[T]:
        return list(self._session.scalars(select(self._model)))
