"""Flask-приложение мини-магазина: фабрика create_app() и маршруты API."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, render_template, request
from werkzeug.security import check_password_hash, generate_password_hash

from app.database import get_connection, init_db
from app.services import (
    apply_discount,
    calculate_total,
    check_stock,
    validate_password,
    validate_username,
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _db_path(app: Flask) -> Path:
    return Path(app.config["DATABASE"])


def create_app(test_config: dict | None = None) -> Flask:
    """Фабрика приложения. test_config позволяет подменить путь к БД в тестах."""
    app = Flask(__name__)
    default_db = Path(__file__).resolve().parent.parent / "app.db"
    app.config.from_mapping(DATABASE=str(default_db))
    if test_config:
        app.config.update(test_config)

    init_db(_db_path(app))

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/api/products")
    def list_products():
        conn = get_connection(_db_path(app))
        try:
            rows = conn.execute(
                "SELECT id, name, price, stock FROM products ORDER BY id"
            ).fetchall()
        finally:
            conn.close()
        return jsonify(
            [
                {
                    "id": r["id"],
                    "name": r["name"],
                    "price": r["price"],
                    "stock": r["stock"],
                }
                for r in rows
            ]
        )

    @app.post("/api/register")
    def register():
        data = request.get_json(silent=True) or {}
        username = data.get("username", "")
        password = data.get("password", "")
        if not isinstance(username, str) or not validate_username(username):
            return jsonify(
                {"error": "Неверный логин: 3–20 символов, латиница, цифры и _"}
            ), 400
        if not isinstance(password, str) or not validate_password(password):
            return (
                jsonify(
                    {
                        "error": "Неверный пароль: минимум 6 символов "
                        "и хотя бы одна цифра"
                    }
                ),
                400,
            )
        conn = get_connection(_db_path(app))
        try:
            conn.execute(
                "INSERT INTO users (username, password_hash, created_at)"
                " VALUES (?, ?, ?)",
                (username, generate_password_hash(password), _now_iso()),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            conn.rollback()
            return jsonify(
                {"error": "Пользователь с таким логином уже существует"}
            ), 400
        finally:
            conn.close()
        return jsonify({"message": "ok"}), 201

    @app.post("/api/login")
    def login():
        data = request.get_json(silent=True) or {}
        username = data.get("username", "")
        password = data.get("password", "")
        conn = get_connection(_db_path(app))
        try:
            row = conn.execute(
                "SELECT * FROM users WHERE username = ?", (username,)
            ).fetchone()
        finally:
            conn.close()
        if row is None or not check_password_hash(row["password_hash"], str(password)):
            return jsonify({"error": "Неверный логин или пароль"}), 401
        return jsonify({"message": "ok"})

    @app.post("/api/orders")
    def create_order():
        data = request.get_json(silent=True) or {}
        user_id = data.get("user_id")
        items = data.get("items")
        promo = data.get("promo")
        if not isinstance(user_id, int) or isinstance(user_id, bool):
            return jsonify({"error": "Не указан user_id"}), 400
        if not isinstance(items, list) or not items:
            return jsonify({"error": "Заказ пуст: добавьте товары"}), 400

        conn = get_connection(_db_path(app))
        try:
            user = conn.execute(
                "SELECT id FROM users WHERE id = ?", (user_id,)
            ).fetchone()
            if user is None:
                return jsonify({"error": "Пользователь не найден"}), 400

            priced_items = []
            for item in items:
                if not isinstance(item, dict):
                    return jsonify({"error": "Неверный формат позиции заказа"}), 400
                product_id = item.get("product_id")
                quantity = item.get("quantity")
                if not isinstance(quantity, int) or isinstance(quantity, bool):
                    return jsonify({"error": "Неверное количество товара"}), 400
                product = conn.execute(
                    "SELECT * FROM products WHERE id = ?", (product_id,)
                ).fetchone()
                if product is None:
                    return jsonify({"error": f"Товар {product_id} не найден"}), 400
                if not check_stock(product["stock"], quantity):
                    return (
                        jsonify({"error": f"Недостаточно товара: {product['name']}"}),
                        400,
                    )
                priced_items.append(
                    {
                        "product_id": product["id"],
                        "price": product["price"],
                        "quantity": quantity,
                    }
                )

            total = apply_discount(calculate_total(priced_items), promo)
            cursor = conn.execute(
                "INSERT INTO orders (user_id, total, created_at) VALUES (?, ?, ?)",
                (user_id, total, _now_iso()),
            )
            order_id = cursor.lastrowid
            for item in priced_items:
                conn.execute(
                    "INSERT INTO order_items (order_id, product_id, quantity, price)"
                    " VALUES (?, ?, ?, ?)",
                    (order_id, item["product_id"], item["quantity"], item["price"]),
                )
                conn.execute(
                    "UPDATE products SET stock = stock - ? WHERE id = ?",
                    (item["quantity"], item["product_id"]),
                )
            conn.commit()
        except ValueError as exc:
            conn.rollback()
            return jsonify({"error": str(exc)}), 400
        finally:
            conn.close()
        return jsonify({"message": "ok", "order_id": order_id, "total": total}), 201

    @app.errorhandler(404)
    def not_found(_exc):
        return jsonify({"error": "Не найдено"}), 404

    @app.errorhandler(405)
    def method_not_allowed(_exc):
        return jsonify({"error": "Метод не разрешён"}), 405

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
