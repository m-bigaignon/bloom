from collections.abc import Callable
from typing import Any, TypeVar

from bloom.events.events import Event


EventT = TypeVar("EventT", bound=Event[Any])


class HandlersRegistry:
    """Registry for event handlers.

    Allows registration of type-safe handlers for specific event types.
    """

    def __init__(self) -> None:
        """Initialize the handlers registry."""
        self.handlers: dict[type[Event[Any]], list[Callable[[Any], None]]] = {}

    def register(
        self, event_type: type[EventT], handler: Callable[[EventT], None]
    ) -> None:
        """Register a handler for a specific event type.

        Args:
            event_type: The event class to handle.
            handler: The handler function that accepts the event.
        """
        if event_type not in self.handlers:
            self.handlers[event_type] = []

        self.handlers[event_type].append(handler)

    def handle(self, event: Event[Any]) -> None:
        """Dispatch an event to all registered handlers.

        Args:
            event: The event to dispatch.
        """
        event_class = type(event)
        if event_class in self.handlers:
            for handler in self.handlers[event_class]:
                handler(event)
