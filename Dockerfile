FROM python:3.6

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . .

ENV PORT="80"
ENV HOST="0.0.0.0"

EXPOSE ${PORT}

CMD ["python", "-m", "app.tools.run_server"]
