from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Self, override

from bloom import repositories, service_layer
from tests.app.adapters.repositories import (
    ProductMemoryRepository,
    ProductSqlaRepository,
)
from tests.app.domain import model


class AbstractProductsUoW(service_layer.AbstractAsyncUOW):
    products: repositories.AsyncRepository[model.Product, str]


class ProductsUoW(AbstractProductsUoW, service_layer.AbstractAsyncSqlaUOW):
    @override
    @asynccontextmanager
    async def __call__(self) -> AsyncGenerator[Self]:
        async with super().__call__() as uow:
            self.products = ProductSqlaRepository(self._session)
            yield uow


class FakeProductsUoW(AbstractProductsUoW, service_layer.AbstractAsyncMemoryUOW):
    def __init__(self) -> None:
        super().__init__()
        self.products = ProductMemoryRepository()

    @override
    @asynccontextmanager
    async def __call__(self) -> AsyncGenerator[Self]:
        async with super().__call__() as uow:
            yield uow
