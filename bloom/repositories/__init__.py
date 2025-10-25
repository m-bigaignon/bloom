"""Infrastructure patterns for DDD implementations."""

from bloom.repositories.abc import AbstractRepository, AsyncAbstractRepository
from bloom.repositories.memory import (
    AsyncInMemoryRepository,
    InMemoryRepository,
)
from bloom.repositories.protocols import (
    AsyncRepository,
    Repository,
)


try:
    from bloom.repositories.sqla import (
        AsyncSqlaRepository,
        SqlaRepository,
    )

    __all__ = [
        "AbstractRepository",
        "AsyncAbstractRepository",
        "AsyncInMemoryRepository",
        "AsyncRepository",
        "AsyncSqlaRepository",
        "InMemoryRepository",
        "Repository",
        "SqlaRepository",
    ]
except ImportError:
    __all__ = [
        "AbstractRepository",
        "AsyncAbstractRepository",
        "AsyncInMemoryRepository",
        "AsyncRepository",
        "InMemoryRepository",
        "Repository",
    ]
