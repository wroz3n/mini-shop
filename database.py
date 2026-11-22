"""Инициализация базы данных SQLite и демо-данные."""

from __future__ import annotations

import sqlite3
from pathlib import Path

DEMO_PRODUCTS = [
    ("Ноутбук", 59999.00, 10),
    ("Мышь", 1499.00, 25),
    ("Клавиатура", 3499.00, 15),
    ("Монитор", 18999.00, 8),
    ("Наушники", 4999.00, 20),
    ("Веб-камера", 2999.00, 12),
]


def get_connection(db_path: str | Path) -> sqlite3.Connection:
    """Возвращает соединение с SQLite с включёнными внешними ключами."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path: str | Path) -> None:
    """Создаёт таблицы, если их нет, и добавляет демо-товары."""
    path = Path(db_path)
    if path.parent and str(path.parent) not in ("", "."):
        path.parent.mkdir(parents=True, exist_ok=True)
    conn = get_connection(path)
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL CHECK (price >= 0),
                stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0)
            );
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id),
                total REAL NOT NULL CHECK (total >= 0),
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL REFERENCES orders(id),
                product_id INTEGER NOT NULL REFERENCES products(id),
                quantity INTEGER NOT NULL CHECK (quantity > 0),
                price REAL NOT NULL CHECK (price >= 0)
            );
            """
        )
        count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        if count == 0:
            conn.executemany(
                "INSERT INTO products (name, price, stock) VALUES (?, ?, ?)",
                DEMO_PRODUCTS,
            )
        conn.commit()
    finally:
        conn.close()
