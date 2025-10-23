from collections.abc import Generator
from contextlib import contextmanager
from typing import Self, override

from bloom import repositories, service_layer
from bloom.repositories.abc import TrackingRepository
from tests.example.app.domain import model


class AbstractProductsUoW(service_layer.AbstractUnitOfWork):
    products: repositories.Repository[model.Product, str]


class ProductsUoW(AbstractProductsUoW, service_layer.AbstractSqlaUnitOfWork):
    @override
    @contextmanager
    def __call__(self) -> Generator[Self]:
        with super().__call__() as uow:
            self.products = TrackingRepository(
                model.Product,
                str,
                repositories.SqlaRepository(model.Product, str, self._session),
            )
            yield uow


class FakeProductsUoW(AbstractProductsUoW, service_layer.AbstractMemoryUnitOfWork):
    def __init__(self) -> None:
        super().__init__()
        self.products = TrackingRepository(
            model.Product,
            str,
            repositories.InMemoryRepository(model.Product, str),
        )

    @override
    @contextmanager
    def __call__(self) -> Generator[Self]:
        with super().__call__() as uow:
            yield uow
