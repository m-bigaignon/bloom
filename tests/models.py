from dataclasses import dataclass
from datetime import date
from typing import Self

from bloom.sara.entities import Entity


@dataclass(frozen=True)
class OrderLine:
    orderid: str
    sku: str
    qty: int


class Batch(Entity[str]):
    def __init__(self, ref: str, sku: str, qty: int, eta: date | None) -> None:
        super().__init__(ref)
        self.sku = sku
        self.eta = eta
        self._initial_quantity = qty
        self._batches = set[OrderLine]()

    @property
    def available_quantity(self) -> int:
        return self._initial_quantity - sum([batch.qty for batch in self._batches])

    def can_allocate(self, line: OrderLine):
        return self.sku == line.sku and self.available_quantity >= line.qty

    def allocate(self, line: OrderLine):
        if self.can_allocate(line):
            self._batches.add(line)

    def deallocate(self, line: OrderLine):
        if line in self._batches:
            self._batches.remove(line)

    def __gt__(self, other: Self):
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta


class OutOfStock(Exception):
    pass


def allocate(line: OrderLine, batches: list[Batch]) -> str:
    try:
        batch = next(b for b in sorted(batches) if b.can_allocate(line))
        batch.allocate(line)
        return batch.id
    except StopIteration:
        raise OutOfStock(f"Out of stock for sku {line.sku}")
