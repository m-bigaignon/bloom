import datetime as dt

import pydantic
from pyrus import Err, Ok, Result

from tests.app.domain import errors, model
from tests.app.service_layer.unit_of_work import AbstractProductsUoW


class BatchData(pydantic.BaseModel):
    ref: str
    sku: str
    qty: int
    eta: dt.date | None = None


class OrderLineData(pydantic.BaseModel):
    orderid: str
    sku: str
    qty: int


async def add_batch(
    data: BatchData,
    uow: AbstractProductsUoW,
) -> None:
    async with uow():
        product = await uow.products.get(data.sku)
        if product is None:
            product = model.Product(data.sku, batches=[])
            uow.products.add(product)

        product.batches.append(model.Batch(**data.model_dump()))
        await uow.commit()


async def allocate(
    line: OrderLineData,
    uow: AbstractProductsUoW,
) -> Result[str, errors.InvalidSkuError | errors.OutOfStockError]:
    new_line = model.OrderLine(**line.model_dump())
    async with uow():
        product = await uow.products.get(line.sku)
        if product is None:
            return Err(errors.InvalidSkuError())

        allocation_result = product.allocate(new_line)
        match allocation_result:
            case Ok(allocation):
                await uow.commit()
                return Ok(allocation)
            case Err(e):
                return Err(e)
