"""."""

from collections.abc import Hashable
from typing import Any, Protocol

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

    def all(self) -> list[T]:
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

    async def all(self) -> list[T]:
        """List all entities in the repository.

        Returns:
            A list of all entities.
        """
        ...
