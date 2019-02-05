FROM python:3.6

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r /app/requirements.txt

ARG DEVTOOLS="False"
COPY requirements-dev.txt .
COPY setup.cfg .
RUN if [ "${DEVTOOLS}" = "True" ]; then pip install --no-cache-dir -r /app/requirements-dev.txt; fi

COPY . .

ENV PORT="80"
ENV HOST="0.0.0.0"

EXPOSE ${PORT}

CMD ["python", "-m", "app.tools.run_server"]
