import uuid
from datetime import date

from fastapi.testclient import TestClient


def random_suffix() -> str:
    return uuid.uuid4().hex[:6]


def random_sku(name: int | str = "") -> str:
    return f"sku-{name}-{random_suffix()}"


def random_batchref(name: int | str = "") -> str:
    return f"batch-{name}-{random_suffix()}"


def random_orderid(name: int | str = "") -> str:
    return f"order-{name}-{random_suffix()}"


def test_happy_path_returns_201(client: TestClient):
    sku, othersku = random_sku(), random_sku("other")
    earlybatch = random_batchref(1)
    laterbatch = random_batchref(2)
    otherbatch = random_batchref(3)
    batches = [
        {
            "ref": laterbatch,
            "sku": sku,
            "qty": 100,
            "eta": date(2025, 1, 2).isoformat(),
        },
        {
            "ref": earlybatch,
            "sku": sku,
            "qty": 100,
            "eta": date(2025, 1, 1).isoformat(),
        },
        {"ref": otherbatch, "sku": othersku, "qty": 100},
    ]
    for batch in batches:
        resp = client.post("/batches/", json=batch)
        assert resp.status_code == 201

    response = client.post(
        "/allocate/", json={"orderid": random_orderid(), "sku": sku, "qty": 3}
    )
    assert response.status_code == 201


def test_unhappy_path_returns_400(client: TestClient):
    unknown_sku, orderid = random_sku(), random_orderid()
    data = {"orderid": orderid, "sku": unknown_sku, "qty": 20}
    response = client.post(
        "/allocate",
        json=data,
    )
    assert response.status_code == 400
