# Dockerfile
FROM python:3.11-slim

# Системные зависимости для psycopg2 и сертификаты
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential \
      libpq-dev \
      ca-certificates \
      openssl \
 && rm -rf /var/lib/apt/lists/* \
 && update-ca-certificates

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код проекта
COPY . .
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Запускаем entrypoint, а затем gunicorn из CMD
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "vacations.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]