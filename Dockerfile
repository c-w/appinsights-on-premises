ARG PYTHON_VERSION=3.8

FROM python:${PYTHON_VERSION} AS builder

WORKDIR /app

COPY requirements/app.txt requirements-app.txt
RUN pip install -r requirements-app.txt \
 && pip wheel -r requirements-app.txt --wheel-dir /deps

COPY requirements/dev.txt requirements-dev.txt
RUN pip install -r requirements-dev.txt

ARG CONNECTOR=postgres
COPY requirements/connectors/${CONNECTOR}.txt requirements-connector.txt
RUN pip install -r requirements-connector.txt \
 && pip wheel -r requirements-connector.txt --wheel-dir /deps

COPY . .

RUN flake8 app
RUN pydocstyle app
RUN isort --quiet --check-only --recursive app
RUN mypy --no-incremental app

FROM python:${PYTHON_VERSION}-slim AS runtime

RUN useradd -ms /bin/sh appinsights

COPY --from=builder /deps /deps
RUN pip install --no-cache-dir /deps/*.whl

COPY --from=builder --chown=appinsights:appinsights /app /app

WORKDIR /app
ENV PORT="8000"
ENV HOST="0.0.0.0"

EXPOSE ${PORT}
USER appinsights

CMD ["python3", "-m", "app.tools.quickstart"]
