"""Classes and utilities to define and deal with values objects.

A Value Object has the following properties:
    - is immutable
    - has structural equality instead of identity equality
    - enforces data validation and type safety
"""

import pydantic


class ValueObject(pydantic.BaseModel):
    """Base class to define a value objects.

    Value objects are simply frozen Pydantic models.
    """

    model_config = pydantic.ConfigDict(frozen=True)
