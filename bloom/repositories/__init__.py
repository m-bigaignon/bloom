"""Infrastructure patterns for DDD implementations."""

from bloom.repositories.abc import Repository, TrackingRepository
from bloom.repositories.memory import InMemoryRepository


try:
    from bloom.repositories.sqla import SqlaRepository

    __all__ = [
        "InMemoryRepository",
        "Repository",
        "SqlaRepository",
        "TrackingRepository",
    ]
except ImportError:
    __all__ = [
        "InMemoryRepository",
        "Repository",
        "TrackingRepository",
    ]
