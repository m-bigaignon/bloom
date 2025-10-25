from tests.app.domain import model
from tests.app.domain.errors import InvalidSkuError
from tests.app.service_layer import services, unit_of_work


async def test_add_batch() -> None:
    uow = unit_of_work.FakeProductsUoW()
    await services.add_batch(
        services.BatchData(ref="b1", sku="CRUNCHY-ARMCHAIR", qty=2, eta=None), uow
    )
    assert uow.committed is True


async def test_returns_allocation() -> None:
    uow = unit_of_work.FakeProductsUoW()
    line = services.OrderLineData(orderid="o1", sku="COMPLICATED-LAMP", qty=10)
    await services.add_batch(
        services.BatchData(ref="b1", sku="COMPLICATED-LAMP", qty=100), uow
    )

    allocation_result = await services.allocate(line, uow)
    assert uow.committed is True
    assert allocation_result.is_ok
    assert allocation_result.unwrap() == "b1"


async def test_error_for_invalid_sku() -> None:
    uow = unit_of_work.FakeProductsUoW()
    line = services.OrderLineData(orderid="o1", sku="NONEXISTENTSKU", qty=10)
    await services.add_batch(services.BatchData(ref="b1", sku="AREALSKU", qty=100), uow)
    new_uow = unit_of_work.FakeProductsUoW()
    assert new_uow.committed is False
    allocation_result = await services.allocate(line, new_uow)
    assert new_uow.committed is False
    assert allocation_result.is_err
    assert isinstance(allocation_result.unwrap_err(), InvalidSkuError)


async def test_uow_tracks_repositories_and_collects_events() -> None:
    uow = unit_of_work.FakeProductsUoW()

    async with uow():
        # Create and add a product
        product = model.Product(
            "LAMP",
            batches=[model.Batch("b1", "LAMP", 100, eta=None)],
        )
        uow.products.add(product)

        # Verify the repository is being tracked by UOW
        assert len(uow._repositories) == 1
        assert hasattr(uow._repositories[0], "tracked")

        # Allocate (this raises an event on the aggregate)
        line = model.OrderLine(orderid="o1", sku="LAMP", qty=10)
        product.allocate(line)

        # Collect events - should find the event from the tracked aggregate
        events = uow.collect_events()
        assert len(events) == 1
        assert events[0].entity_id == "LAMP"
