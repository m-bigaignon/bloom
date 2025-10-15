"""Define domain events related functions."""

import uuid
from collections.abc import Hashable
from typing import TypeVar

import pydantic


EntityId = TypeVar("EntityId", bound=Hashable)


class Event[EntityId](pydantic.BaseModel):
    """Base class for domain events."""

    event_id: uuid.UUID = pydantic.Field(default_factory=uuid.uuid4)
    entity_id: EntityId
