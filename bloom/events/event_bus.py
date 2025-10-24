"""Event bus implementations for synchronous and asynchronous event handling."""

import asyncio
import logging
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

from bloom.events.events import Event


EventT = TypeVar("EventT", bound=Event[Any])
logger = logging.getLogger(__name__)


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


class AsyncHandlersRegistry:
    """Registry for async event handlers.

    Allows registration of type-safe async handlers for specific event types.
    Handlers are dispatched concurrently, and errors are logged without
    interrupting other handlers.
    """

    def __init__(self) -> None:
        """Initialize the async handlers registry."""
        self.handlers: dict[
            type[Event[Any]], list[Callable[[Any], Awaitable[None]]]
        ] = {}

    def register(
        self, event_type: type[EventT], handler: Callable[[EventT], Awaitable[None]]
    ) -> None:
        """Register an async handler for a specific event type.

        Args:
            event_type: The event class to handle.
            handler: The async handler function that accepts the event.
        """
        if event_type not in self.handlers:
            self.handlers[event_type] = []

        self.handlers[event_type].append(handler)

    async def handle(self, event: Event[Any]) -> None:
        """Dispatch an event to all registered async handlers concurrently.

        Handlers are executed in parallel using asyncio.gather with
        return_exceptions=True. Any exceptions raised by handlers are logged
        but do not prevent other handlers from executing.

        Args:
            event: The event to dispatch.
        """
        event_class = type(event)
        if event_class in self.handlers:
            results = await asyncio.gather(
                *[handler(event) for handler in self.handlers[event_class]],
                return_exceptions=True,
            )

            for idx, result in enumerate(results):
                if isinstance(result, Exception):
                    handler = self.handlers[event_class][idx]
                    logger.exception(
                        "Handler %s failed for event %s",
                        handler.__name__,
                        event_class.__name__,
                        exc_info=result,
                    )
