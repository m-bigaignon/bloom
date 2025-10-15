from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import sqlalchemy as sqla
from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import sessionmaker

from tests.example.app.adapters import orm
from tests.example.app.domain import model
from tests.example.app.service_layer import services, unit_of_work


engine = sqla.create_engine("sqlite:///main.db", echo=False)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None]:
    with orm.start_mappers() as registry:
        registry.metadata.create_all(engine)
        yield
        registry.metadata.drop_all(engine)


session_maker = sessionmaker(bind=engine)
app = FastAPI(lifespan=lifespan)


@app.post("/batches/", status_code=201)
def create_batch(data: services.BatchData) -> None:
    uow = unit_of_work.ProductsUoW(session_maker)
    return services.add_batch(data, uow)


@app.post("/allocate/", status_code=201)
def allocate_endpoint(line: services.OrderLineData) -> dict[str, str]:
    uow = unit_of_work.ProductsUoW(session_maker)
    try:
        batchref = services.allocate(line, uow)
    except (model.OutOfStockError, services.InvalidSkuError) as e:
        raise HTTPException(400, {"message": str(e)}) from e
    return {"batchref": batchref}
