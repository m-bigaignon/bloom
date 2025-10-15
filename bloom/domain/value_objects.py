"""Classes and utilities to define and deal with values objects.

A Value Object has the following properties:
    - is immutable
    - has structural equality instead of identity equality
    - enforces data validation and type safety
"""

from dataclasses import dataclass
from typing import Any, dataclass_transform, override


@dataclass_transform()
class ValueObject:
    """Base class that provides dataclass-like behavior with immutability."""

    @override
    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)

        # Check if user defined their own __post_init__
        user_post_init = cls.__dict__.get("__post_init__", None)

        # Create wrapped __post_init__ that ensures _finalize_init is called
        if user_post_init is not None:

            def wrapped_post_init(self: ValueObject) -> None:
                user_post_init(self)
                self._finalize_init()

            cls.__post_init__ = wrapped_post_init  # type: ignore [attr-defined]
        else:

            def default_post_init(self: ValueObject) -> None:
                self._finalize_init()

            cls.__post_init__ = default_post_init  # type: ignore [attr-defined]

        # Apply dataclass decorator automatically
        dataclass(unsafe_hash=True)(cls)

    @override
    def __setattr__(self, name: str, value: Any) -> None:
        if not hasattr(self, "_init_complete"):
            object.__setattr__(self, name, value)
        else:
            msg = f"Cannot modify immutable instance: attribute '{name}' is read-only"
            raise AttributeError(msg)

    @override
    def __delattr__(self, name: str) -> None:
        msg = "Cannot delete attribute from immutable instance"
        raise AttributeError(msg)

    def _finalize_init(self) -> None:
        """Mark initialization as complete."""
        object.__setattr__(self, "_init_complete", True)
