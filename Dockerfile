FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app

CMD ["sh", "-c", "while ! nc -z db 5432; do sleep 1; done && \
                  while ! nc -z redis 6379; do sleep 1; done && \
                  alembic upgrade head && \
                  uvicorn app.main:app --host ${APP_HOST} --port ${APP_PORT} --reload"]