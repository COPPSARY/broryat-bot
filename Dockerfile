FROM python:3.13-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

COPY main.py ./
COPY bot ./bot

RUN uv sync --frozen --no-dev

FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app
COPY --from=builder /app /app
ENV UV_LINK_MODE=copy PATH="/app/.venv/bin:$PATH"

EXPOSE 8080

CMD ["uv", "run", "--frozen", "--no-dev", "main.py"]
