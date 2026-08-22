import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def create_product(client: AsyncClient, payload: dict) -> dict:
    response = await client.post("/products", json=payload)
    assert response.status_code == 201
    return response.json()


async def test_create_product(client: AsyncClient, product_payload: dict):
    response = await client.post("/products", json=product_payload)

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == product_payload["name"]
    assert body["price"] == product_payload["price"]
    assert body["quantity"] == product_payload["quantity"]
    assert "id" in body


async def test_create_product_invalid_price(client: AsyncClient, product_payload: dict):
    product_payload["price"] = -5
    response = await client.post("/products", json=product_payload)

    assert response.status_code == 422


async def test_list_products_empty(client: AsyncClient):
    response = await client.get("/products")

    assert response.status_code == 200
    assert response.json() == []


async def test_list_products(client: AsyncClient, product_payload: dict):
    await create_product(client, product_payload)
    await create_product(client, {**product_payload, "name": "Mouse"})

    response = await client.get("/products")

    assert response.status_code == 200
    names = {p["name"] for p in response.json()}
    assert names == {"Keyboard", "Mouse"}


async def test_get_product(client: AsyncClient, product_payload: dict):
    created = await create_product(client, product_payload)

    response = await client.get(f"/products/{created['id']}")

    assert response.status_code == 200
    assert response.json() == created


async def test_get_product_not_found(client: AsyncClient):
    response = await client.get("/products/999")

    assert response.status_code == 404


async def test_update_product(client: AsyncClient, product_payload: dict):
    created = await create_product(client, product_payload)

    response = await client.put(f"/products/{created['id']}", json={"price": 149.99})

    assert response.status_code == 200
    body = response.json()
    assert body["price"] == 149.99
    assert body["name"] == product_payload["name"]


async def test_update_product_not_found(client: AsyncClient):
    response = await client.put("/products/999", json={"price": 10})

    assert response.status_code == 404


async def test_delete_product(client: AsyncClient, product_payload: dict):
    created = await create_product(client, product_payload)

    response = await client.delete(f"/products/{created['id']}")
    assert response.status_code == 204

    response = await client.get(f"/products/{created['id']}")
    assert response.status_code == 404


async def test_delete_product_not_found(client: AsyncClient):
    response = await client.delete("/products/999")

    assert response.status_code == 404
