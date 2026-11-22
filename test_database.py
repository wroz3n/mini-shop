"""Тесты БД: создание таблиц, ограничения, внешние ключи."""

import sqlite3
from datetime import datetime, timezone

import pytest

from app.database import DEMO_PRODUCTS, init_db


def test_tables_created_and_demo_products_seeded(db_conn):
    tables = {
        row[0]
        for row in db_conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    assert {"users", "products", "orders", "order_items"} <= tables
    count = db_conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    assert count == len(DEMO_PRODUCTS)
    names = [r[0] for r in db_conn.execute("SELECT name FROM products").fetchall()]
    assert "Ноутбук" in names


def test_init_db_is_idempotent(db_path):
    init_db(db_path)
    init_db(db_path)
    conn = sqlite3.connect(str(db_path))
    try:
        count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    finally:
        conn.close()
    assert count == len(DEMO_PRODUCTS)


def test_username_unique_constraint(db_conn):
    now = datetime.now(timezone.utc).isoformat()
    db_conn.execute(
        "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
        ("unique_user", "hash", now),
    )
    db_conn.commit()
    with pytest.raises(sqlite3.IntegrityError):
        db_conn.execute(
            "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
            ("unique_user", "hash", now),
        )


def test_negative_product_price_rejected_by_check(db_conn):
    with pytest.raises(sqlite3.IntegrityError):
        db_conn.execute(
            "INSERT INTO products (name, price, stock) VALUES (?, ?, ?)",
            ("Брак", -10.0, 1),
        )


def test_negative_stock_rejected_by_check(db_conn):
    with pytest.raises(sqlite3.IntegrityError):
        db_conn.execute(
            "INSERT INTO products (name, price, stock) VALUES (?, ?, ?)",
            ("Брак", 10.0, -1),
        )


def test_order_with_unknown_user_rejected_by_foreign_key(db_conn):
    now = datetime.now(timezone.utc).isoformat()
    with pytest.raises(sqlite3.IntegrityError):
        db_conn.execute(
            "INSERT INTO orders (user_id, total, created_at) VALUES (?, ?, ?)",
            (999, 100.0, now),
        )


def test_order_item_quantity_must_be_positive(db_conn):
    now = datetime.now(timezone.utc).isoformat()
    db_conn.execute(
        "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
        ("buyer", "hash", now),
    )
    db_conn.execute(
        "INSERT INTO orders (user_id, total, created_at) VALUES (?, ?, ?)",
        (1, 10.0, now),
    )
    with pytest.raises(sqlite3.IntegrityError):
        db_conn.execute(
            "INSERT INTO order_items (order_id, product_id, quantity, price)"
            " VALUES (?, ?, ?, ?)",
            (1, 1, 0, 10.0),
        )
