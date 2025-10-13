import datetime as dt
from collections.abc import Sequence

import pydantic

from tests.example.domain import model
from tests.example.service_layer.unit_of_work import AbstractBatchesUoW


class InvalidSku(Exception):
    pass


class BatchData(pydantic.BaseModel):
    ref: str
    sku: str
    qty: int
    eta: dt.date | None = None


class OrderLineData(pydantic.BaseModel):
    orderid: str
    sku: str
    qty: int


class FakeSession:
    def __init__(self) -> None:
        self.committed = False

    def commit(self):
        self.committed = True


def is_valid_sku(sku: str, batches: Sequence[model.Batch]) -> bool:
    return sku in {b.sku for b in batches}


def allocate(
    line: OrderLineData,
    uow: AbstractBatchesUoW,
):
    new_line = model.OrderLine(**line.model_dump())
    with uow():
        batches = uow.batches.list()
        if not is_valid_sku(line.sku, batches):
            raise InvalidSku

        allocation = model.allocate(new_line, batches)
        uow.commit()
        return allocation


def add_batch(
    data: BatchData,
    uow: AbstractBatchesUoW,
) -> str:
    with uow():
        new_batch = model.Batch(**data.model_dump())
        uow.batches.add(new_batch)
        uow.commit()
        return new_batch.id
