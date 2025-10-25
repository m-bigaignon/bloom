from typing import override

from sqlalchemy import orm, select
from sqlalchemy.ext import asyncio

from bloom.repositories import memory, sqla
from tests.app.domain import model


class ProductSqlaRepository(sqla.AsyncSqlaRepository):
    def __init__(self, session: asyncio.AsyncSession):
        super().__init__(model.Product, str, session)

    @override
    async def _get(self, entity_id: str) -> model.Product | None:
        return await self._session.scalar(
            select(model.Product)
            .where(self._model._id == entity_id)
            .options(orm.selectinload(model.Product.batches))
        )


class ProductMemoryRepository(memory.AsyncInMemoryRepository):
    def __init__(self):
        super().__init__(model.Product, str)
