"""Юнит-тесты бизнес-логики (app/services.py)."""

import pytest

from app.services import (
    apply_discount,
    calculate_total,
    check_stock,
    validate_password,
    validate_username,
)


# calculate_total
def test_calculate_total_typical_items():
    items = [{"price": 100.0, "quantity": 2}, {"price": 50.5, "quantity": 3}]
    assert calculate_total(items) == 351.5


def test_calculate_total_empty_list_returns_zero():
    assert calculate_total([]) == 0.0


def test_calculate_total_single_item():
    assert calculate_total([{"price": 999.99, "quantity": 1}]) == 999.99


def test_calculate_total_rounds_to_two_decimals():
    assert calculate_total([{"price": 10.005, "quantity": 3}]) == 30.02


def test_calculate_total_negative_price_raises_value_error():
    with pytest.raises(ValueError):
        calculate_total([{"price": -1.0, "quantity": 1}])


def test_calculate_total_zero_quantity_raises_value_error():
    with pytest.raises(ValueError):
        calculate_total([{"price": 10.0, "quantity": 0}])


def test_calculate_total_negative_quantity_raises_value_error():
    with pytest.raises(ValueError):
        calculate_total([{"price": 10.0, "quantity": -2}])


# check_stock
def test_check_stock_enough():
    assert check_stock(10, 3) is True


def test_check_stock_exactly_enough():
    assert check_stock(5, 5) is True


def test_check_stock_not_enough():
    assert check_stock(2, 5) is False


def test_check_stock_zero_stock():
    assert check_stock(0, 1) is False


def test_check_stock_zero_quantity_raises_value_error():
    with pytest.raises(ValueError):
        check_stock(10, 0)


def test_check_stock_negative_quantity_raises_value_error():
    with pytest.raises(ValueError):
        check_stock(10, -1)


# apply_discount
def test_apply_discount_sale10_gives_ten_percent_off():
    assert apply_discount(1000.0, "SALE10") == 900.0


def test_apply_discount_wrong_promo_no_discount():
    assert apply_discount(1000.0, "WRONG") == 1000.0


def test_apply_discount_empty_promo_no_discount():
    assert apply_discount(1000.0, "") == 1000.0


def test_apply_discount_none_promo_no_discount():
    assert apply_discount(1000.0, None) == 1000.0


def test_apply_discount_result_never_negative():
    assert apply_discount(0.0, "SALE10") == 0.0


def test_apply_discount_promo_is_case_sensitive():
    assert apply_discount(1000.0, "sale10") == 1000.0


# validate_username
def test_validate_username_valid():
    assert validate_username("user_1") is True


def test_validate_username_too_short():
    assert validate_username("ab") is False


def test_validate_username_too_long():
    assert validate_username("a" * 21) is False


def test_validate_username_cyrillic_is_false():
    assert validate_username("пользователь") is False


def test_validate_username_space_is_false():
    assert validate_username("user name") is False


def test_validate_username_min_length_ok():
    assert validate_username("abc") is True


def test_validate_username_max_length_ok():
    assert validate_username("a" * 20) is True


# validate_password
def test_validate_password_valid():
    assert validate_password("pass123") is True


def test_validate_password_too_short():
    assert validate_password("a1b2") is False


def test_validate_password_no_digit_is_false():
    assert validate_password("password") is False


def test_validate_password_min_length_with_digit_ok():
    assert validate_password("abcde1") is True
