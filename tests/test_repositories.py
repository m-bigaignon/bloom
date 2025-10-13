"""Tests for repository implementations."""

import datetime as dt

import pytest

from bloom.prajnan import InMemoryRepository
from bloom.sara.entities import Entity
from tests.example.domain.model import Batch, OrderLine


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
