import pytest

from bloom.domain import ValueObject


class Data(ValueObject):
    qty: int
    name: str


def test_value_objects_are_immutable() -> None:
    data = Data(qty=12, name="CUSHION_BLUE")
    with pytest.raises(AttributeError):
        data.qty = 10


def test_value_objects_have_structural_equality() -> None:
    data1 = Data(qty=12, name="CUSHION_BLUE")
    data2 = Data(qty=12, name="CUSHION_BLUE")
    assert data1 == data2
