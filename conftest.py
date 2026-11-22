"""Фикстуры: временная БД, тестовое приложение, тестовый клиент."""

import pytest

from app.database import get_connection, init_db
from app.main import create_app


@pytest.fixture()
def db_path(tmp_path):
    path = tmp_path / "test.db"
    init_db(path)
    return path


@pytest.fixture()
def app(db_path):
    return create_app({"DATABASE": str(db_path), "TESTING": True})


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def db_conn(db_path):
    conn = get_connection(db_path)
    yield conn
    conn.close()


@pytest.fixture()
def user_id(client):
    resp = client.post(
        "/api/register", json={"username": "testuser", "password": "pass123"}
    )
    assert resp.status_code == 201
    # id первого пользователя во временной БД — 1
    return 1
