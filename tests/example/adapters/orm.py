from collections import abc
from contextlib import contextmanager

import sqlalchemy as sqla
from sqlalchemy import orm

from tests.example.domain import model


registry = orm.registry()

order_lines = sqla.Table(
    "order_lines",
    registry.metadata,
    sqla.Column("id", sqla.String(255), nullable=False, primary_key=True),
    sqla.Column("sku", sqla.String(255), nullable=False),
    sqla.Column("qty", sqla.Integer, nullable=False),
)

batches = sqla.Table(
    "batches",
    registry.metadata,
    sqla.Column("id", sqla.String(255), nullable=False, primary_key=True),
    sqla.Column("sku", sqla.String(255), nullable=False),
    sqla.Column("eta", sqla.Date, nullable=True),
    sqla.Column("initial_quantity", sqla.Integer, nullable=False),
)

allocations = sqla.Table(
    "allocations",
    registry.metadata,
    sqla.Column("orderline_id", sqla.ForeignKey("order_lines.id"), primary_key=True),
    sqla.Column("batch_id", sqla.ForeignKey("batches.id"), primary_key=True),
)


@contextmanager
def start_mappers() -> abc.Generator[orm.registry]:
    registry.map_imperatively(
        model.OrderLine,
        order_lines,
        properties={
            "_id": order_lines.c.id,
        },
    )
    registry.map_imperatively(
        model.Batch,
        batches,
        properties={
            "_id": batches.c.id,
            "_initial_quantity": batches.c.initial_quantity,
            "_allocations": orm.relationship(
                model.OrderLine, secondary=allocations, collection_class=set
            ),
        },
    )
    try:
        yield registry
    finally:
        registry.dispose()
