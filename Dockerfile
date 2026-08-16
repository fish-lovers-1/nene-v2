FROM python:3.14-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependency files first for caching
COPY nene-bot/pyproject.toml nene-bot/uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev --no-install-project

# Copy the Python project
COPY nene-bot/ ./

# Install the project
RUN uv sync --frozen --no-dev

CMD ["uv", "run", "python", "main.py"]
