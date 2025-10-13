import datetime as dt
from collections.abc import Sequence

import pydantic

from tests.example.domain import model
from tests.example.service_layer.unit_of_work import AbstractProductsUoW


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


def add_batch(
    data: BatchData,
    uow: AbstractProductsUoW,
):
    with uow():
        product = uow.products.get(data.sku)
        if product is None:
            product = model.Product(data.sku, batches=[])
            uow.products.add(product)

        product.batches.append(model.Batch(**data.model_dump()))
        uow.commit()


def allocate(
    line: OrderLineData,
    uow: AbstractProductsUoW,
) -> str:
    new_line = model.OrderLine(**line.model_dump())
    with uow():
        product = uow.products.get(line.sku)
        if product is None:
            raise InvalidSku

        allocation = product.allocate(new_line)
        uow.commit()
        return allocation
