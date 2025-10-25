from datetime import date
from typing import Self

from pyrus import Err, Ok, Result

from bloom import domain
from tests.app.domain import errors, events


class OrderLine(domain.ValueObject):
    orderid: str
    sku: str
    qty: int


class Batch(domain.Entity[str]):
    def __init__(self, ref: str, sku: str, qty: int, eta: date | None) -> None:
        super().__init__(ref)
        self.sku = sku
        self.eta = eta
        self._initial_quantity = qty
        self._allocations = set[OrderLine]()

    @property
    def available_quantity(self) -> int:
        return self._initial_quantity - sum([batch.qty for batch in self._allocations])

    def can_allocate(self, line: OrderLine) -> bool:
        return self.sku == line.sku and self.available_quantity >= line.qty

    def allocate(self, line: OrderLine) -> None:
        if self.can_allocate(line):
            self._allocations.add(line)

    def deallocate(self, line: OrderLine) -> None:
        if line in self._allocations:
            self._allocations.remove(line)

    def __gt__(self, other: Self) -> bool:
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta


class Product(domain.Aggregate[str]):
    def __init__(self, sku: str, batches: list[Batch]):
        super().__init__(sku)
        self.batches = batches

    def allocate(self, line: OrderLine) -> Result[str, errors.OutOfStockError]:
        try:
            batch = next(b for b in sorted(self.batches) if b.can_allocate(line))
            self.raise_event(events.Allocate(entity_id=self.id))
            batch.allocate(line)
        except StopIteration:
            msg = f"Out of stock for sku {line.sku}"
            return Err(errors.OutOfStockError(msg))
        return Ok(batch.id)
