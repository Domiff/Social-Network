dev:
    uv run fastapi dev src/main.py

revision msg:
    uv run alembic revision --autogenerate -m "{{msg}}"

upgrade:
    uv run alembic upgrade head

test *args:
    uv run pytest {{args}}

lint:
    uv run ruff check . --fix

format:
    uv run ruff format .
