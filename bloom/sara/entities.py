"""Basic entities management."""

from abc import ABC
from collections.abc import Hashable
from typing import TypeVar, override


EntityId = TypeVar("EntityId", bound=Hashable)


class Entity[EntityId](ABC):
    """A basic Entity."""

    def __init__(self, entity_id: EntityId) -> None:
        """Initialize a brand new entity."""
        self._id: EntityId = entity_id

    @property
    def id(self) -> EntityId:
        """The unique identity of this entity."""
        return self._id

    @override
    def __eq__(self, other: object) -> bool:
        """Compare two entities.

        Entities are considered equals if the have the same type and id.
        """
        if not isinstance(other, Entity):
            return False
        return type(self) is not type(other) and self.id == other.id

    @override
    def __hash__(self) -> int:
        """Computes a hash based on entity type and id."""
        return hash((type(self), self.id))
