from collections.abc import Generator
from contextlib import contextmanager
from typing import Self, override

from bloom.prajnan import repositories, uow
from tests.example.domain import model


class AbstractBatchesUoW(uow.AbstractUnitOfWork):
    batches: repositories.Repository[model.Batch, str]


class BatchesUoW(AbstractBatchesUoW, uow.AbstractSqlaUnitOfWork):
    @override
    @contextmanager
    def __call__(self) -> Generator[Self]:
        with super().__call__() as uow:
            self.batches = repositories.SqlaRepository(model.Batch, str, self._session)
            yield uow


class FakeBatchesUoW(AbstractBatchesUoW, uow.AbstractMemoryUnitOfWork):
    def __init__(self) -> None:
        super().__init__()
        self.batches = repositories.InMemoryRepository(model.Batch, str)

    @override
    @contextmanager
    def __call__(self) -> Generator[Self]:
        with super().__call__() as uow:
            yield uow
