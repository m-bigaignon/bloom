"""Basic entities management."""

from collections.abc import Hashable
from typing import TypeVar, override


EntityId = TypeVar("EntityId", bound=Hashable)


class Entity[EntityId]:
    """A basic Entity."""

    _id: EntityId

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
        return isinstance(other, type(self)) and self.id == other.id

    @override
    def __hash__(self) -> int:
        """Computes a hash based on entity type and id."""
        return hash((type(self), self.id))

    @override
    def __repr__(self) -> str:
        """Returns a string representation of the entity."""
        return f"{self.__class__!s}(id={self._id!r})"
