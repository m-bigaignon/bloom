import pydantic
import pytest

from bloom.sara.value_objects import ValueObject


class Data(ValueObject):
    qty: int
    name: str


class NestedData(ValueObject):
    sku: str
    batches: list[Data]


def test_value_objects_are_immutable() -> None:
    data = Data(qty=12, name="CUSHION_BLUE")
    with pytest.raises(pydantic.ValidationError):  # type: ignore [misc]
        data.qty = 10  # type: ignore [misc]


def test_value_objects_have_structural_equality() -> None:
    data1 = Data(qty=12, name="CUSHION_BLUE")
    data2 = Data(qty=12, name="CUSHION_BLUE")
    assert data1 == data2
