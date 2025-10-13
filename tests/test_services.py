import pytest

from tests.example.service_layer import services, unit_of_work


def test_add_batch():
    uow = unit_of_work.FakeBatchesUoW()
    res = services.add_batch(
        services.BatchData(ref="b1", sku="CRUNCHY-ARMCHAIR", qty=2, eta=None), uow
    )
    assert uow.committed is True
    assert res == "b1"


def test_returns_allocation():
    uow = unit_of_work.FakeBatchesUoW()
    line = services.OrderLineData(orderid="o1", sku="COMPLICATED-LAMP", qty=10)
    services.add_batch(
        services.BatchData(ref="b1", sku="COMPLICATED-LAMP", qty=100), uow
    )

    res = services.allocate(line, uow)
    assert uow.committed is True
    assert res == "b1"


def test_error_for_invalid_sku():
    uow = unit_of_work.FakeBatchesUoW()
    line = services.OrderLineData(orderid="o1", sku="NONEXISTENTSKU", qty=10)
    services.add_batch(services.BatchData(ref="b1", sku="AREALSKU", qty=100), uow)
    with pytest.raises(services.InvalidSku):
        _ = services.allocate(line, uow)
