"""Classes and utilities to define and deal with values objects."""

import pydantic


class ValueObject(pydantic.BaseModel):
    """Base class to define a value objects.

    Value objects are frozen Pydantic models.
    """

    model_config = pydantic.ConfigDict(frozen=True)
