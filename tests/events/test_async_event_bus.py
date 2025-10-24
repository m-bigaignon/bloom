import asyncio
import logging
from unittest.mock import AsyncMock

import pytest
from _pytest.logging import LogCaptureFixture

from bloom.events import AsyncHandlersRegistry, Event


class SampleEvent(Event[str]):
    """Test event for testing."""

    event_type: str = "test.event"
    entity_id: str


class AnotherSampleEvent(Event[int]):
    """Another test event."""

    event_type: str = "another.event"
    entity_id: int


@pytest.fixture
def anyio_backend() -> str:
    """Use asyncio backend for tests."""
    return "asyncio"


@pytest.fixture
def event_bus() -> AsyncHandlersRegistry:
    """Create a fresh async event bus for each test."""
    return AsyncHandlersRegistry()


async def test_register_and_handle_single_handler(
    event_bus: AsyncHandlersRegistry,
) -> None:
    """Test registering and handling a single async handler."""
    handled_events: list[SampleEvent] = []

    async def handler(event: SampleEvent) -> None:
        handled_events.append(event)

    event_bus.register(SampleEvent, handler)
    event = SampleEvent(entity_id="test-123")

    await event_bus.handle(event)

    assert len(handled_events) == 1
    assert handled_events[0] == event


async def test_register_multiple_handlers_for_same_event(
    event_bus: AsyncHandlersRegistry,
) -> None:
    """Test multiple handlers for the same event type execute concurrently."""
    handler1_called = asyncio.Event()
    handler2_called = asyncio.Event()
    results: list[str] = []

    async def handler1(_event: SampleEvent) -> None:
        results.append("handler1")
        handler1_called.set()

    async def handler2(_event: SampleEvent) -> None:
        results.append("handler2")
        handler2_called.set()

    event_bus.register(SampleEvent, handler1)
    event_bus.register(SampleEvent, handler2)
    event = SampleEvent(entity_id="test-123")

    await event_bus.handle(event)

    # Both handlers should have been called
    assert handler1_called.is_set()
    assert handler2_called.is_set()
    assert len(results) == 2
    assert set(results) == {"handler1", "handler2"}


async def test_handlers_run_concurrently(event_bus: AsyncHandlersRegistry) -> None:
    """Test that handlers run concurrently, not sequentially."""
    execution_order: list[str] = []

    async def slow_handler(_event: SampleEvent) -> None:
        execution_order.append("slow_start")
        await asyncio.sleep(0.1)
        execution_order.append("slow_end")

    async def fast_handler(_event: SampleEvent) -> None:
        execution_order.append("fast_start")
        await asyncio.sleep(0.01)
        execution_order.append("fast_end")

    event_bus.register(SampleEvent, slow_handler)
    event_bus.register(SampleEvent, fast_handler)
    event = SampleEvent(entity_id="test-123")

    await event_bus.handle(event)

    # If concurrent, fast handler should complete before slow handler
    # Both should start before either finishes
    assert "fast_start" in execution_order
    assert "slow_start" in execution_order
    assert "fast_end" in execution_order
    assert "slow_end" in execution_order
    # Fast should finish before slow
    assert execution_order.index("fast_end") < execution_order.index("slow_end")


async def test_different_event_types_have_separate_handlers(
    event_bus: AsyncHandlersRegistry,
) -> None:
    """Test that different event types have separate handler registrations."""
    test_events: list[SampleEvent] = []
    another_events: list[AnotherSampleEvent] = []

    async def test_handler(event: SampleEvent) -> None:
        test_events.append(event)

    async def another_handler(event: AnotherSampleEvent) -> None:
        another_events.append(event)

    event_bus.register(SampleEvent, test_handler)
    event_bus.register(AnotherSampleEvent, another_handler)

    test_event = SampleEvent(entity_id="test-123")
    another_event = AnotherSampleEvent(entity_id=456)

    await event_bus.handle(test_event)
    await event_bus.handle(another_event)

    assert len(test_events) == 1
    assert len(another_events) == 1
    assert test_events[0] == test_event
    assert another_events[0] == another_event


async def test_handler_exception_does_not_stop_other_handlers(
    event_bus: AsyncHandlersRegistry,
    caplog: LogCaptureFixture,
) -> None:
    """Test that exception in one handler doesn't prevent others from running."""
    successful_handler_called = False

    async def failing_handler(_event: SampleEvent) -> None:
        msg = "Handler intentionally failed"
        raise ValueError(msg)

    async def successful_handler(_event: SampleEvent) -> None:
        nonlocal successful_handler_called
        successful_handler_called = True

    event_bus.register(SampleEvent, failing_handler)
    event_bus.register(SampleEvent, successful_handler)
    event = SampleEvent(entity_id="test-123")

    with caplog.at_level(logging.ERROR):
        await event_bus.handle(event)

    # Successful handler should still have been called
    assert successful_handler_called

    # Error should have been logged
    assert "Handler intentionally failed" in caplog.text
    assert "failing_handler" in caplog.text


async def test_multiple_handler_exceptions_all_logged(
    event_bus: AsyncHandlersRegistry,
    caplog: LogCaptureFixture,
) -> None:
    """Test that all handler exceptions are logged."""

    async def failing_handler1(_event: SampleEvent) -> None:
        msg = "First failure"
        raise ValueError(msg)

    async def failing_handler2(_event: SampleEvent) -> None:
        msg = "Second failure"
        raise RuntimeError(msg)

    event_bus.register(SampleEvent, failing_handler1)
    event_bus.register(SampleEvent, failing_handler2)
    event = SampleEvent(entity_id="test-123")

    with caplog.at_level(logging.ERROR):
        await event_bus.handle(event)

    # Both errors should be logged
    assert "First failure" in caplog.text
    assert "Second failure" in caplog.text
    assert "failing_handler1" in caplog.text
    assert "failing_handler2" in caplog.text


async def test_handle_with_no_registered_handlers(
    event_bus: AsyncHandlersRegistry,
) -> None:
    """Test handling event with no registered handlers does nothing."""
    event = SampleEvent(entity_id="test-123")

    # Should not raise any exception
    await event_bus.handle(event)


async def test_handler_can_be_async_mock(event_bus: AsyncHandlersRegistry) -> None:
    """Test that AsyncMock can be used as a handler (useful for testing)."""
    mock_handler = AsyncMock()

    event_bus.register(SampleEvent, mock_handler)
    event = SampleEvent(entity_id="test-123")

    await event_bus.handle(event)

    mock_handler.assert_called_once_with(event)
