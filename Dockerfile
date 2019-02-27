ARG PYTHON_VERSION=3.7

FROM python:${PYTHON_VERSION} AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip wheel --no-cache-dir -r requirements.txt --wheel-dir /deps

COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

COPY . .

RUN flake8 app
RUN isort --quiet --check-only --recursive app
RUN mypy --no-incremental app

FROM python:${PYTHON_VERSION}-slim AS runtime

COPY --from=builder /deps /deps
RUN pip install --no-cache-dir /deps/*.whl

COPY --from=builder /app /app

WORKDIR /app
ENV PORT="80"
ENV HOST="0.0.0.0"

EXPOSE ${PORT}

CMD ["python", "-m", "app.tools.quickstart"]
