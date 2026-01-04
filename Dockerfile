FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /code

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN apt-get update \
 && apt-get install -y --no-install-recommends curl \
 && rm -rf /var/lib/apt/lists/*

# forced
ENV UV_INDEX_URL=https://pypi.org/simple
ENV PIP_INDEX_URL=https://pypi.org/simple

COPY pyproject.toml uv.lock /code/
RUN uv sync --frozen --no-dev

COPY app /code/app

EXPOSE 8000
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
