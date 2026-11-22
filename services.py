"""Чистая бизнес-логика магазина (без Flask) — удобно тестировать."""

from __future__ import annotations

import re

PROMO_CODE = "SALE10"
PROMO_DISCOUNT = 0.10
_USERNAME_RE = re.compile(r"^[A-Za-z0-9_]{3,20}$")


def calculate_total(items: list[dict]) -> float:
    """Сумма заказа: price * quantity по каждой позиции, округление до 2 знаков.

    Пустой список — 0.0. Отрицательная цена или количество <= 0 — ValueError.
    """
    total = 0.0
    for item in items:
        price = item["price"]
        quantity = item["quantity"]
        if price < 0:
            raise ValueError("Цена не может быть отрицательной")
        if quantity <= 0:
            raise ValueError("Количество должно быть больше нуля")
        total += price * quantity
    return round(total, 2)


def check_stock(product_stock: int, quantity: int) -> bool:
    """True, если остатка хватает для заказанного количества."""
    if quantity <= 0:
        raise ValueError("Количество должно быть больше нуля")
    return product_stock >= quantity


def apply_discount(total: float, promo: str | None) -> float:
    """Промокод SALE10 даёт скидку 10%, любой другой или пустой — без скидки."""
    if promo == PROMO_CODE:
        total = total * (1 - PROMO_DISCOUNT)
    return round(max(total, 0.0), 2)


def validate_username(username: str) -> bool:
    """True, только если 3–20 символов: латинские буквы, цифры и '_'."""
    if not isinstance(username, str):
        return False
    return bool(_USERNAME_RE.match(username))


def validate_password(password: str) -> bool:
    """True, только если длина не менее 6 символов и есть хотя бы одна цифра."""
    if not isinstance(password, str):
        return False
    return len(password) >= 6 and any(ch.isdigit() for ch in password)
