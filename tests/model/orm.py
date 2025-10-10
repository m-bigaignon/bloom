from sqlalchemy import Column, Date, ForeignKey, Integer, String, Table
from sqlalchemy.orm import registry, relationship

from tests.model.models import Batch, OrderLine


mapper_registry = registry()

order_lines = Table(
    "order_lines",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("sku", String(255), nullable=False),
    Column("qty", Integer, nullable=False),
    Column("orderid", String(255), nullable=False),
)

batches = Table(
    "batches",
    mapper_registry.metadata,
    Column("ref", String(255), nullable=False, primary_key=True),
    Column("sku", String(255), nullable=False),
    Column("eta", Date, nullable=True),
    Column("_initial_quantity", Integer, nullable=False),
)

allocations = Table(
    "allocations",
    mapper_registry.metadata,
    Column("orderline_id", ForeignKey("order_lines.id"), primary_key=True),
    Column("batch_id", ForeignKey("batches.id"), primary_key=True),
)


def start_mappers():
    mapper_registry.map_imperatively(OrderLine, order_lines)
    mapper_registry.map_imperatively(
        Batch,
        batches,
        properties={
            "_allocations": relationship(
                OrderLine, secondary=allocations, collection_class=set
            )
        },
    )
