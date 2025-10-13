from collections.abc import Generator
from contextlib import contextmanager
from typing import Self, override

from bloom.prajnan import repositories, uow
from tests.example.domain import model


class AbstractProductsUoW(uow.AbstractUnitOfWork):
    products: repositories.Repository[model.Product, str]


class ProductsUoW(AbstractProductsUoW, uow.AbstractSqlaUnitOfWork):
    @override
    @contextmanager
    def __call__(self) -> Generator[Self]:
        with super().__call__() as uow:
            self.batches = repositories.SqlaRepository(
                model.Product, str, self._session
            )
            yield uow


class FakeProductsUoW(AbstractProductsUoW, uow.AbstractMemoryUnitOfWork):
    def __init__(self) -> None:
        super().__init__()
        self.products = repositories.InMemoryRepository(model.Product, str)

    @override
    @contextmanager
    def __call__(self) -> Generator[Self]:
        with super().__call__() as uow:
            yield uow
