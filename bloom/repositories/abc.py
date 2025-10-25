"""Abstract classes for repository pattern."""

from abc import abstractmethod
from collections.abc import Hashable
from types import get_original_bases
from typing import Any, get_args, get_origin

from bloom import domain


class RepositoryBase[T: domain.Entity[Any], E: Hashable]:
    """Base repository class."""

    def __init__(self, entity_type: type[T], id_type: type[E]):
        """Construct a basic repository."""
        RepositoryBase.validate_types(entity_type, id_type)
        self._tracked: set[T] = set()

    @property
    def tracked(self) -> set[T]:
        """Return the set of tracked entities.

        Returns:
            A copy of the tracked entities set.
        """
        return self._tracked.copy()

    @classmethod
    def validate_types(cls, entity_type: type[T], id_type: type[E]) -> None:
        """Placeholder."""
        if get_origin(entity_type) in (domain.Entity, domain.Aggregate):
            base = entity_type
            args = get_args(base)
            if len(args) == 0 or args[0] is not id_type:
                msg = "Typing mismatch for repository"
                raise TypeError(msg)
        else:
            type_ = (
                get_origin(entity_type)
                if get_origin(entity_type) is not None
                else entity_type
            )
            assert isinstance(type_, type)
            bases = get_original_bases(type_)
            for base in bases:
                cls.validate_types(base, id_type)


class AbstractRepository[T: domain.Entity[Any], E: Hashable](RepositoryBase):
    """Repository that tracks seen aggregates."""

    def add(self, entity: T) -> None:
        """Add a new entity to the repository.

        Args:
            entity: The entity to add.
        """
        self._tracked.add(entity)
        self._add(entity)

    def get(self, entity_id: E) -> T | None:
        """Retrieve an entity by its ID.

        Args:
            entity_id: The unique identifier of the entity.

        Returns:
            The entity if found, None otherwise.
        """
        result = self._get(entity_id)
        if result is not None:
            self._tracked.add(result)
        return result

    def all(self) -> list[T]:
        """List all entities in the repository.

        Returns:
            A list of all entities.
        """
        res = self._all()
        self._tracked.update(res)
        return res

    @abstractmethod
    def _add(self, entity: T) -> None: ...

    @abstractmethod
    def _get(self, entity_id: E) -> T | None: ...

    @abstractmethod
    def _all(self) -> list[T]: ...


class AsyncAbstractRepository[T: domain.Entity[Any], E: Hashable](RepositoryBase):
    """Mixin to add entity tracking to async repositories.

    This mixin tracks entities that are retrieved via get() or added via add().
    It can be mixed with any AsyncRepository implementation to enable tracking.
    """

    def add(self, entity: T) -> None:
        """Add a new entity to the repository.

        Args:
            entity: The entity to add.
        """
        self._tracked.add(entity)
        self._add(entity)

    async def get(self, entity_id: E) -> T | None:
        """Retrieve an entity by its ID.

        Args:
            entity_id: The unique identifier of the entity.

        Returns:
            The entity if found, None otherwise.
        """
        result = await self._get(entity_id)
        if result is not None:
            self._tracked.add(result)
        return result

    async def all(self) -> list[T]:
        """List all entities in the repository.

        Returns:
            A list of all entities.
        """
        res = await self._all()
        self._tracked.update(res)
        return res

    @abstractmethod
    def _add(self, entity: T) -> None: ...

    @abstractmethod
    async def _get(self, entity_id: E) -> T | None: ...

    @abstractmethod
    async def _all(self) -> list[T]: ...
