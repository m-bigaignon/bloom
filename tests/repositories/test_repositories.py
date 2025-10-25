"""Tests for repository implementations."""

import datetime as dt

import pytest

from bloom.domain import Entity
from bloom.repositories import InMemoryRepository
from tests.app.domain.model import Batch, OrderLine


today = dt.datetime.now(dt.UTC).date()


def make_batch_and_line(
    sku: str, batch_qty: int, line_qty: int
) -> tuple[Batch, OrderLine]:
    return (
        Batch("batch-001", sku, batch_qty, eta=today),
        OrderLine(orderid="order-123", sku=sku, qty=line_qty),
    )


class SpecialBatch[T](Batch):
    pass


class TestInMemoryRepository:
    """Tests for InMemoryRepository."""

    def test_type_validity(self) -> None:
        _ = InMemoryRepository(Entity[int], int)
        _ = InMemoryRepository(Batch, str)
        _ = InMemoryRepository(SpecialBatch[str], str)

    def test_can_add_and_retrieve_entity(self) -> None:
        """Test that entities can be added and retrieved by ID."""
        repo = InMemoryRepository(Batch, str)
        large_batch, _ = make_batch_and_line("ELEGANT-LAMP", 20, 2)

        repo.add(large_batch)
        retrieved = repo.get("batch-001")

        assert retrieved is not None
        assert retrieved.id == "batch-001"

    def test_get_returns_none_for_nonexistent_entity(self) -> None:
        """Test that get returns None when entity doesn't exist."""
        repo = InMemoryRepository(Batch, str)

        result = repo.get("nonexistent")

        assert result is None

    def test_can_remove_entity(self) -> None:
        """Test that entities can be removed from the repository."""
        repo = InMemoryRepository(Batch, str)

        large_batch, _ = make_batch_and_line("ELEGANT-LAMP", 20, 2)
        repo.add(large_batch)
        repo.remove("batch-001")
        retrieved = repo.get("batch-001")

        assert retrieved is None

    def test_remove_nonexistent_entity_does_not_raise(self) -> None:
        """Test that removing a nonexistent entity doesn't raise an error."""
        repo = InMemoryRepository(Batch, str)

        repo.remove("nonexistent")  # Should not raise

    @pytest.mark.skip
    def test_can_list_all_entities(self) -> None:
        """Test that all entities can be listed."""

    @pytest.mark.skip
    def test_list_returns_empty_list_when_no_entities(self) -> None:
        """Test that list returns empty list when repository is empty."""

    @pytest.mark.skip
    def test_adding_entity_with_same_id_overwrites_previous(self) -> None:
        """Test that adding an entity with the same ID replaces the old one."""


class TestTrackingInMemoryRepository:
    """Tests for TrackingInMemoryRepository using mixin approach."""

    def test_tracks_added_entities(self) -> None:
        """Test that added entities are tracked."""
        repo = InMemoryRepository(Batch, str)
        batch, _ = make_batch_and_line("ELEGANT-LAMP", 20, 2)

        repo.add(batch)

        assert batch in repo.tracked
        assert len(repo.tracked) == 1

    def test_tracks_retrieved_entities(self) -> None:
        """Test that retrieved entities are tracked."""
        repo = InMemoryRepository(Batch, str)
        batch, _ = make_batch_and_line("ELEGANT-LAMP", 20, 2)

        repo.add(batch)
        # Clear tracking to test get() tracking
        repo._tracked.clear()
        retrieved = repo.get("batch-001")

        assert retrieved is not None
        assert retrieved in repo.tracked
        assert len(repo.tracked) == 1

    def test_get_nonexistent_does_not_track(self) -> None:
        """Test that getting a nonexistent entity doesn't add to tracked."""
        repo = InMemoryRepository(Batch, str)

        result = repo.get("nonexistent")

        assert result is None
        assert len(repo.tracked) == 0

    def test_tracked_returns_copy(self) -> None:
        """Test that tracked property returns a copy, not the internal set."""
        repo = InMemoryRepository(Batch, str)
        batch, _ = make_batch_and_line("ELEGANT-LAMP", 20, 2)

        repo.add(batch)
        tracked1 = repo.tracked
        tracked2 = repo.tracked

        # Should be equal but not the same object
        assert tracked1 == tracked2
        assert tracked1 is not tracked2
        # Should not be the internal set
        assert tracked1 is not repo._tracked

    def test_can_use_all_repository_methods(self) -> None:
        """Test that tracking repository supports all base repository methods."""
        repo = InMemoryRepository(Batch, str)
        batch1, _ = make_batch_and_line("LAMP", 20, 2)
        batch2 = Batch("batch-002", "TABLE", 15, eta=today)

        # Add
        repo.add(batch1)
        repo.add(batch2)

        # Get
        retrieved = repo.get("batch-001")
        assert retrieved is not None

        # List
        all_batches = repo.all()
        assert len(all_batches) == 2

        # Remove
        repo.remove("batch-001")
        assert repo.get("batch-001") is None

    def test_multiple_gets_track_same_entity_once(self) -> None:
        """Test that getting the same entity multiple times only tracks it once."""
        repo = InMemoryRepository(Batch, str)
        batch, _ = make_batch_and_line("ELEGANT-LAMP", 20, 2)

        repo.add(batch)
        # Clear to isolate get tracking
        repo._tracked.clear()

        repo.get("batch-001")
        repo.get("batch-001")
        repo.get("batch-001")

        # Should only be tracked once (sets eliminate duplicates)
        assert len(repo.tracked) == 1
