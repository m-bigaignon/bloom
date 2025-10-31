from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pyrus import Err, Ok
from sqlalchemy.ext import asyncio

from bloom.events.event_bus import HandlersRegistry
from bloom.redbird.sqlrepo import SQLARepo
from tests.app.adapters import orm
from tests.app.domain import events
from tests.app.domain.model import Product
from tests.app.service_layer import services, unit_of_work


engine = asyncio.create_async_engine("sqlite+aiosqlite:///main.db", echo=False)


def handle_allocate(event: events.Allocate) -> None:
    print(event)  # noqa: T201


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None]:
    HandlersRegistry().register(events.Allocate, handle_allocate)
    with orm.start_mappers() as registry:
        async with engine.begin() as conn:
            await conn.run_sync(registry.metadata.drop_all)
            await conn.run_sync(registry.metadata.create_all)
        yield


session_maker = asyncio.async_sessionmaker(bind=engine)
app = FastAPI(lifespan=lifespan)


@app.post("/batches/", status_code=201)
async def create_batch(data: services.BatchData) -> None:
    uow = unit_of_work.ProductsUoW(session_maker)
    await services.add_batch(data, uow)


@app.post("/allocate/", status_code=201)
async def allocate_endpoint(line: services.OrderLineData) -> dict[str, str]:
    uow = unit_of_work.ProductsUoW(session_maker)
    batchref = await services.allocate(line, uow)
    match batchref:
        case Ok(batchref):
            return {"batchref": batchref}
        case Err(e):
            raise HTTPException(400, {"message": str(e)}) from e


@app.get("/test-repo")
async def test_repo() -> str:
    product_repo = SQLARepo(Product)
    print(product_repo.all().filter(batches__sku="eoa").stmt)
    return "blbl"
