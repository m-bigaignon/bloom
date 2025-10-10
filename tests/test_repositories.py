"""Tests for repository implementations."""

import uuid
from collections.abc import Hashable

from bloom.parijata import Event
from bloom.prajnan import EventPublishingRepository, InMemoryRepository
from bloom.sara import Aggregate, Entity


class FakeEntity(Entity[str]):
    """Fake entity for repository tests."""

    def __init__(self, entity_id: str, value: str) -> None:
        """Initialize fake entity."""
        super().__init__(entity_id)
        self.value = value


class FakeEvent(Event[Hashable]):
    """Fake event for event publishing tests."""

    action: str


class FakeAggregate(Aggregate[Hashable]):
    """Fake aggregate for event publishing tests."""

    def __init__(self, entity_id: str, value: str) -> None:
        """Initialize fake aggregate."""
        super().__init__(entity_id)
        self.value = value

    def do_something(self) -> None:
        """Perform an action that raises a domain event."""
        self.raise_event(FakeEvent(entity_id=self.id, action="something_done"))


class TestInMemoryRepository:
    """Tests for InMemoryRepository."""

    def test_can_add_and_retrieve_entity(self) -> None:
        """Test that entities can be added and retrieved by ID."""
        repo = InMemoryRepository[FakeEntity]()
        entity = FakeEntity("test-1", "value-1")

        repo.add(entity)
        retrieved = repo.get("test-1")

        assert retrieved is not None
        assert retrieved.id == "test-1"
        assert retrieved.value == "value-1"

    def test_get_returns_none_for_nonexistent_entity(self) -> None:
        """Test that get returns None when entity doesn't exist."""
        repo = InMemoryRepository[FakeEntity]()

        result = repo.get("nonexistent")

        assert result is None

    def test_can_remove_entity(self) -> None:
        """Test that entities can be removed from the repository."""
        repo = InMemoryRepository[FakeEntity]()
        entity = FakeEntity("test-1", "value-1")

        repo.add(entity)
        repo.remove("test-1")
        retrieved = repo.get("test-1")

        assert retrieved is None

    def test_remove_nonexistent_entity_does_not_raise(self) -> None:
        """Test that removing a nonexistent entity doesn't raise an error."""
        repo = InMemoryRepository[FakeEntity]()

        repo.remove("nonexistent")  # Should not raise

    def test_can_list_all_entities(self) -> None:
        """Test that all entities can be listed."""
        repo = InMemoryRepository[FakeEntity]()
        entity1 = FakeEntity("test-1", "value-1")
        entity2 = FakeEntity("test-2", "value-2")
        entity3 = FakeEntity("test-3", "value-3")

        repo.add(entity1)
        repo.add(entity2)
        repo.add(entity3)
        entities = repo.list()

        assert len(entities) == 3
        assert entity1 in entities
        assert entity2 in entities
        assert entity3 in entities

    def test_list_returns_empty_list_when_no_entities(self) -> None:
        """Test that list returns empty list when repository is empty."""
        repo = InMemoryRepository[FakeEntity]()

        entities = repo.list()

        assert entities == []

    def test_adding_entity_with_same_id_overwrites_previous(self) -> None:
        """Test that adding an entity with the same ID replaces the old one."""
        repo = InMemoryRepository[FakeEntity]()
        entity1 = FakeEntity("test-1", "value-1")
        entity2 = FakeEntity("test-1", "value-2")

        repo.add(entity1)
        repo.add(entity2)
        retrieved = repo.get("test-1")

        assert retrieved is not None
        assert retrieved.value == "value-2"
        assert len(repo.list()) == 1


class TestEventPublishingRepository:
    """Tests for EventPublishingRepository."""

    def test_publishes_events_when_aggregate_added(self) -> None:
        """Test that events are published when an aggregate is added."""
        base_repo = InMemoryRepository[FakeAggregate]()
        published_events: list[Event[Hashable]] = []

        def publish_event(event: Event[Hashable]) -> None:
            published_events.append(event)

        repo = EventPublishingRepository(base_repo, publish_event)
        aggregate = FakeAggregate("agg-1", "test")
        aggregate.do_something()

        repo.add(aggregate)

        assert len(published_events) == 1
        assert isinstance(published_events[0], FakeEvent)
        assert published_events[0].action == "something_done"
        assert published_events[0].entity_id == "agg-1"

    def test_flushes_events_after_publishing(self) -> None:
        """Test that events are flushed after being published."""
        base_repo = InMemoryRepository[FakeAggregate]()
        published_events: list[Event[Hashable]] = []

        def publish_event(event: Event[Hashable]) -> None:
            published_events.append(event)

        repo = EventPublishingRepository(base_repo, publish_event)
        aggregate = FakeAggregate("agg-1", "test")
        aggregate.do_something()

        repo.add(aggregate)
        retrieved = repo.get("agg-1")

        assert retrieved is not None
        assert retrieved.pending_events == []

    def test_publishes_multiple_events(self) -> None:
        """Test that multiple events are published."""
        base_repo = InMemoryRepository[FakeAggregate]()
        published_events: list[Event[Hashable]] = []

        def publish_event(event: Event[Hashable]) -> None:
            published_events.append(event)

        repo = EventPublishingRepository(base_repo, publish_event)
        aggregate = FakeAggregate("agg-1", "test")
        aggregate.do_something()
        aggregate.do_something()
        aggregate.do_something()

        repo.add(aggregate)

        assert len(published_events) == 3

    def test_does_not_publish_events_when_none_raised(self) -> None:
        """Test that no events are published when aggregate has no events."""
        base_repo = InMemoryRepository[FakeAggregate]()
        published_events: list[Event[Hashable]] = []

        def publish_event(event: Event[Hashable]) -> None:
            published_events.append(event)

        repo = EventPublishingRepository(base_repo, publish_event)
        aggregate = FakeAggregate("agg-1", "test")

        repo.add(aggregate)

        assert len(published_events) == 0

    def test_get_delegates_to_base_repository(self) -> None:
        """Test that get method delegates to the base repository."""
        base_repo = InMemoryRepository[FakeAggregate]()
        repo = EventPublishingRepository(base_repo, lambda _: None)
        aggregate = FakeAggregate("agg-1", "test")

        base_repo.add(aggregate)
        retrieved = repo.get("agg-1")

        assert retrieved is not None
        assert retrieved.id == "agg-1"

    def test_remove_delegates_to_base_repository(self) -> None:
        """Test that remove method delegates to the base repository."""
        base_repo = InMemoryRepository[FakeAggregate]()
        repo = EventPublishingRepository(base_repo, lambda _: None)
        aggregate = FakeAggregate("agg-1", "test")

        base_repo.add(aggregate)
        repo.remove("agg-1")
        retrieved = base_repo.get("agg-1")

        assert retrieved is None

    def test_list_delegates_to_base_repository(self) -> None:
        """Test that list method delegates to the base repository."""
        base_repo = InMemoryRepository[FakeAggregate]()
        repo = EventPublishingRepository(base_repo, lambda _: None)
        agg1 = FakeAggregate("agg-1", "test1")
        agg2 = FakeAggregate("agg-2", "test2")

        base_repo.add(agg1)
        base_repo.add(agg2)
        aggregates = repo.list()

        assert len(aggregates) == 2
        assert agg1 in aggregates
        assert agg2 in aggregates

    def test_event_ids_are_unique(self) -> None:
        """Test that each published event has a unique ID."""
        base_repo = InMemoryRepository[FakeAggregate]()
        published_events: list[Event[Hashable]] = []

        def publish_event(event: Event[Hashable]) -> None:
            published_events.append(event)

        repo = EventPublishingRepository(base_repo, publish_event)
        aggregate = FakeAggregate("agg-1", "test")
        aggregate.do_something()
        aggregate.do_something()

        repo.add(aggregate)

        event_ids = [event.event_id for event in published_events]
        assert len(event_ids) == 2
        assert event_ids[0] != event_ids[1]
        assert all(isinstance(eid, uuid.UUID) for eid in event_ids)
