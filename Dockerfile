# Используем Python 3.11-slim в качестве базового образа
FROM python:3.11-slim

# Устанавливаем системные пакеты для сборки psycopg2
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential \
      libpq-dev \
 && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код проекта
COPY . .

# Собираем статику
RUN python manage.py collectstatic --noinput

# Открываем порт приложения
EXPOSE 8000

# Запускаем Gunicorn
CMD ["gunicorn", "vacations.wsgi:application", "--bind", "0.0.0.0:8000"]