"""Abstract classes for repository pattern."""

from collections.abc import Hashable
from types import get_original_bases
from typing import Any, Protocol, get_args, get_origin

from bloom import domain


class Repository[T: domain.Entity[Any], E: Hashable](Protocol):
    """Base abstract class defining the repository interface for entities.

    Repositories provide an abstraction over data persistence,
    allowing domain logic to remain independent of infrastructure concerns.

    Type Parameters:
        T: The entity type this repository manages (must have id: EntityIdT)
    """

    def add(self, entity: T) -> None:
        """Add a new entity to the repository.

        Args:
            entity: The entity to add.
        """
        ...

    def get(self, entity_id: E) -> T | None:
        """Retrieve an entity by its ID.

        Args:
            entity_id: The unique identifier of the entity.

        Returns:
            The entity if found, None otherwise.
        """
        ...

    def remove(self, entity_id: E) -> None:
        """Remove an entity from the repository.

        Args:
            entity_id: The unique identifier of the entity to remove.
        """
        ...

    def list(self) -> list[T]:
        """List all entities in the repository.

        Returns:
            A list of all entities.
        """
        ...


class AsyncRepository[T: domain.Entity[Any], E: Hashable](Protocol):
    """Base abstract class defining the repository interface for entities.

    Repositories provide an abstraction over data persistence,
    allowing domain logic to remain independent of infrastructure concerns.

    Type Parameters:
        T: The entity type this repository manages (must have id: EntityIdT)
    """

    def add(self, entity: T) -> None:
        """Add a new entity to the repository.

        Args:
            entity: The entity to add.
        """
        ...

    async def get(self, entity_id: E) -> T | None:
        """Retrieve an entity by its ID.

        Args:
            entity_id: The unique identifier of the entity.

        Returns:
            The entity if found, None otherwise.
        """
        ...

    async def remove(self, entity_id: E) -> None:
        """Remove an entity from the repository.

        Args:
            entity_id: The unique identifier of the entity to remove.
        """
        ...

    async def list(self) -> list[T]:
        """List all entities in the repository.

        Returns:
            A list of all entities.
        """
        ...


class BaseRepository[T: domain.Entity[Any], E: Hashable]:
    """Base repository class."""

    def __init__(self, entity_type: type[T], id_type: type[E]):
        """Construct a basic repository."""
        BaseRepository._validate_types(entity_type, id_type)

    @classmethod
    def _validate_types(cls, entity_type: type[T], id_type: type[E]) -> None:
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
                cls._validate_types(base, id_type)


class TrackingRepository[T: domain.Entity[Any], E: Hashable](BaseRepository[T, E]):
    """Placeholder."""

    def __init__(self, entity_type: type[T], id_type: type[E], repo: Repository[T, E]):
        """Placeholder."""
        super().__init__(entity_type, id_type)
        self._tracked: set[T] = set()
        self._repo = repo

    @property
    def tracked(self) -> set[T]:
        """Return the set of tracked entities.

        Returns:
            A copy of the tracked entities set.
        """
        return self._tracked.copy()

    def add(self, entity: T) -> None:
        """Placeholder."""
        self._tracked.add(entity)
        self._repo.add(entity)

    def get(self, entity_id: E) -> T | None:
        """Placeholder."""
        res = self._repo.get(entity_id)
        if res is not None:
            self._tracked.add(res)
        return res

    def remove(self, entity_id: E) -> None:
        """Placeholder."""
        self._repo.remove(entity_id)

    def list(self) -> list[T]:
        """Placeholder."""
        return self._repo.list()


class AsyncTrackingRepository[T: domain.Entity[Any], E: Hashable](BaseRepository[T, E]):
    """Placeholder."""

    def __init__(
        self, entity_type: type[T], id_type: type[E], repo: AsyncRepository[T, E]
    ):
        """Placeholder."""
        super().__init__(entity_type, id_type)
        self._tracked: set[T] = set()
        self._repo = repo

    @property
    def tracked(self) -> set[T]:
        """Return the set of tracked entities.

        Returns:
            A copy of the tracked entities set.
        """
        return self._tracked.copy()

    def add(self, entity: T) -> None:
        """Placeholder."""
        self._tracked.add(entity)
        self._repo.add(entity)

    async def get(self, entity_id: E) -> T | None:
        """Placeholder."""
        res = await self._repo.get(entity_id)
        if res is not None:
            self._tracked.add(res)
        return res

    async def remove(self, entity_id: E) -> None:
        """Placeholder."""
        await self.remove(entity_id)

    async def list(self) -> list[T]:
        """Placeholder."""
        return await self._repo.list()
