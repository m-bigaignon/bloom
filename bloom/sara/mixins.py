from collections.abc import Callable
from functools import wraps
from typing import Any, Concatenate, Protocol, TypeVar, cast

import option


class SupportsStateTracking(Protocol):
    @property
    def is_dirty(self) -> bool: ...
    def set_dirty(self) -> None: ...
    def set_clean(self) -> None: ...


F = TypeVar(
    "F",
    bound=Callable[Concatenate[SupportsStateTracking, ...], option.Result[Any, Any]],
)


class StateTrackingMixin:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._is_dirty: bool = False

    @property
    def is_dirty(self) -> bool:
        return self._is_dirty

    def set_dirty(self) -> None:
        self._is_dirty = True

    def set_clean(self) -> None:
        self._is_dirty = False


def mutates(func: F) -> F:
    @wraps(func)
    def wrapper(obj: SupportsStateTracking, *args: Any, **kwargs: Any) -> Any:
        result = func(obj, *args, **kwargs)
        if result.is_ok and hasattr(obj, "set_dirty"):
            obj.set_dirty()
        return result

    return cast("F", wrapper)
