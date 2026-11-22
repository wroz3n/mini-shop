"""Интеграционные тесты API через Flask test_client."""

from app.database import get_connection


def test_get_products_returns_200_and_demo_products(client):
    resp = client.get("/api/products")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) >= 5
    names = [p["name"] for p in data]
    assert "Ноутбук" in names
    assert all({"id", "name", "price", "stock"} <= set(p) for p in data)


def test_index_page_returns_200(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "Мини-магазин" in resp.get_data(as_text=True)


def test_register_success_returns_201(client):
    resp = client.post(
        "/api/register", json={"username": "newuser", "password": "secret1"}
    )
    assert resp.status_code == 201
    assert resp.get_json()["message"] == "ok"


def test_register_duplicate_username_returns_400(client):
    client.post("/api/register", json={"username": "dupuser", "password": "secret1"})
    resp = client.post(
        "/api/register", json={"username": "dupuser", "password": "secret1"}
    )
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_register_short_password_returns_400(client):
    resp = client.post("/api/register", json={"username": "shortpw", "password": "a1"})
    assert resp.status_code == 400


def test_register_invalid_username_returns_400(client):
    resp = client.post("/api/register", json={"username": "ab", "password": "secret1"})
    assert resp.status_code == 400


def test_login_success_returns_200(client):
    client.post("/api/register", json={"username": "loginuser", "password": "secret1"})
    resp = client.post(
        "/api/login", json={"username": "loginuser", "password": "secret1"}
    )
    assert resp.status_code == 200
    assert resp.get_json()["message"] == "ok"


def test_login_wrong_password_returns_401(client):
    client.post("/api/register", json={"username": "loginuser2", "password": "secret1"})
    resp = client.post(
        "/api/login", json={"username": "loginuser2", "password": "wrong99"}
    )
    assert resp.status_code == 401


def test_login_unknown_user_returns_401(client):
    resp = client.post("/api/login", json={"username": "nobody", "password": "secret1"})
    assert resp.status_code == 401


def test_create_order_success_decreases_stock(client, user_id, db_path):
    before = client.get("/api/products").get_json()
    stock_before = next(p["stock"] for p in before if p["id"] == 1)
    resp = client.post(
        "/api/orders",
        json={"user_id": user_id, "items": [{"product_id": 1, "quantity": 2}]},
    )
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["total"] == 119998.0
    conn = get_connection(db_path)
    try:
        stock_after = conn.execute(
            "SELECT stock FROM products WHERE id = 1"
        ).fetchone()[0]
        order_count = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    finally:
        conn.close()
    assert stock_after == stock_before - 2
    assert order_count == 1


def test_create_order_with_promo_applies_discount(client, user_id):
    resp = client.post(
        "/api/orders",
        json={
            "user_id": user_id,
            "items": [{"product_id": 2, "quantity": 1}],
            "promo": "SALE10",
        },
    )
    assert resp.status_code == 201
    assert resp.get_json()["total"] == 1349.1


def test_create_order_unknown_product_returns_400(client, user_id):
    resp = client.post(
        "/api/orders",
        json={"user_id": user_id, "items": [{"product_id": 999, "quantity": 1}]},
    )
    assert resp.status_code == 400


def test_create_order_more_than_stock_returns_400(client, user_id):
    resp = client.post(
        "/api/orders",
        json={"user_id": user_id, "items": [{"product_id": 4, "quantity": 999}]},
    )
    assert resp.status_code == 400


def test_create_order_unknown_user_returns_400(client):
    resp = client.post(
        "/api/orders",
        json={"user_id": 999, "items": [{"product_id": 1, "quantity": 1}]},
    )
    assert resp.status_code == 400


def test_create_order_empty_items_returns_400(client, user_id):
    resp = client.post("/api/orders", json={"user_id": user_id, "items": []})
    assert resp.status_code == 400
