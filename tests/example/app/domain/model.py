from datetime import date
from typing import Self

from bloom import domain


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

    def allocate(self, line: OrderLine) -> str:
        try:
            batch = next(b for b in sorted(self.batches) if b.can_allocate(line))
            batch.allocate(line)
        except StopIteration as err:
            msg = f"Out of stock for sku {line.sku}"
            raise OutOfStockError(msg) from err
        return batch.id


class OutOfStockError(Exception):
    pass
