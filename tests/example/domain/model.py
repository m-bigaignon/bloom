from datetime import date
from typing import Self

from bloom.sara.entities import Entity


class OrderLine(Entity[str]):
    def __init__(self, orderid: str, sku: str, qty: int) -> None:
        super().__init__(orderid)
        self.sku = sku
        self.qty = qty


class Batch(Entity[str]):
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


class OutOfStockError(Exception):
    pass


def allocate(line: OrderLine, batches: list[Batch]) -> str:
    try:
        batch = next(b for b in sorted(batches) if b.can_allocate(line))
        batch.allocate(line)
    except StopIteration as err:
        msg = f"Out of stock for sku {line.sku}"
        raise OutOfStockError(msg) from err
    return batch.id
