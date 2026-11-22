# Мини-магазин

![CI](https://github.com/<username>/mini-shop/actions/workflows/ci.yml/badge.svg)

Минимальный интернет-магазин на Flask + SQLite с модулем тестирования и CI/CD-пайплайном (GitHub Actions).

## Стек

- Python 3.12
- Flask 3.x
- SQLite (встроенный модуль `sqlite3`, файл `app.db`)
- pytest + pytest-cov — тесты и покрытие
- ruff — линтер
- GitHub Actions — CI/CD

## Как запустить локально

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate
pip install -r requirements.txt
flask --app "app.main:create_app" run
```

Откройте http://127.0.0.1:5000 — главная страница «Мини-магазин», список товаров загружается с `GET /api/products`. При первом запуске база `app.db` создаётся автоматически и заполняется 6 демо-товарами.

## API

- `GET /` — главная страница
- `GET /api/products` — список товаров: `id`, `name`, `price`, `stock`
- `POST /api/register` — `{"username": ..., "password": ...}`, успех — `201`
- `POST /api/login` — `{"username": ..., "password": ...}`, успех — `200`, неверные данные — `401`
- `POST /api/orders` — `{"user_id": ..., "items": [{"product_id": ..., "quantity": ...}], "promo": "SALE10"}`, успех — `201`

Все ошибки API возвращают JSON `{"error": "..."}` на русском.

Промокод `SALE10` даёт скидку 10%.

## Как запустить тесты

```bash
pip install -r requirements-dev.txt
pytest -v
pytest --cov=app --cov-report=term-missing
ruff check app tests
```

Покрытие кода — не менее 80% (`--cov-fail-under=80`).

## Как работает пайплайн

При каждом `push` и `pull_request` в ветку `main` запускается GitHub Actions (`.github/workflows/ci.yml`), результат — во вкладке **Actions** репозитория:

1. **Job `test`**: установка Python 3.12, зависимостей, `ruff check app tests`, тесты с покрытием `pytest --cov=app --cov-fail-under=80`, проверка, что приложение стартует (`create_app()`).
2. **Job `build`** (после `test`): архивирует исходники без `app.db`, `__pycache__` и `.venv` и загружает артефакт `mini-shop`.

## Как сделать push на GitHub

```bash
git add .
git commit -m "Описание изменений"
git push
```

Если репозиторий ещё не создан, сначала создайте его на GitHub (имя `mini-shop`), затем:

```bash
git init
git branch -M main
git remote add origin https://github.com/<username>/mini-shop.git
git push -u origin main
```

