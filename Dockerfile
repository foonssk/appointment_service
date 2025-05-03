FROM python:3.9-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем только requirements.txt сначала для кэширования
COPY requirements.txt .

# Установка Python-зависимостей с четким указанием версий
RUN pip install --upgrade pip && \
    pip install --no-cache-dir \
    python-telegram-bot==20.3 \
    apscheduler==3.10.1 \
    -r requirements.txt

# Копируем весь проект
COPY . .

ENV PYTHONPATH=/app

CMD ["sh", "-c", "while ! nc -z db 5432; do sleep 1; done && \
                  while ! nc -z redis 6379; do sleep 1; done && \
                  alembic upgrade head && \
                  uvicorn app.main:app --host ${APP_HOST} --port ${APP_PORT} --reload"]