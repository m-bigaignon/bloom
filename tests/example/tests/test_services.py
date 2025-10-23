from tests.example.app.domain.errors import InvalidSkuError
from tests.example.app.service_layer import services, unit_of_work


def test_add_batch() -> None:
    uow = unit_of_work.FakeProductsUoW()
    services.add_batch(
        services.BatchData(ref="b1", sku="CRUNCHY-ARMCHAIR", qty=2, eta=None), uow
    )
    assert uow.committed is True


def test_returns_allocation() -> None:
    uow = unit_of_work.FakeProductsUoW()
    line = services.OrderLineData(orderid="o1", sku="COMPLICATED-LAMP", qty=10)
    services.add_batch(
        services.BatchData(ref="b1", sku="COMPLICATED-LAMP", qty=100), uow
    )

    allocation_result = services.allocate(line, uow)
    assert uow.committed is True
    assert allocation_result.is_ok
    assert allocation_result.unwrap() == "b1"


def test_error_for_invalid_sku() -> None:
    uow = unit_of_work.FakeProductsUoW()
    line = services.OrderLineData(orderid="o1", sku="NONEXISTENTSKU", qty=10)
    services.add_batch(services.BatchData(ref="b1", sku="AREALSKU", qty=100), uow)
    new_uow = unit_of_work.FakeProductsUoW()
    assert new_uow.committed is False
    allocation_result = services.allocate(line, new_uow)
    assert new_uow.committed is False
    assert allocation_result.is_err
    assert isinstance(allocation_result.unwrap_err(), InvalidSkuError)
