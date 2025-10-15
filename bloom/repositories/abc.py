"""Abstract classes for repository pattern."""

import abc
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


class BaseRepository[T: domain.Entity[Any], E: Hashable](Repository[T, E]):
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
