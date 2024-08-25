# Используем официальный Python образ
FROM python:3.11

ENV PYTHONUNBUFFERED=1

# Устанавливаем и запускаем CRON
RUN apt-get update && apt-get install -y cron

# Устанавливаем Poetry
RUN pip install --upgrade pip "poetry==1.8.3"
RUN poetry config virtualenvs.create false

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем pyproject.toml и poetry.lock и устанавливаем зависимости
COPY pyproject.toml pyproject.toml
COPY poetry.lock poetry.lock

# Устанавливаем зависимости проекта
RUN poetry install --without dev --no-root

RUN poetry show

# Копируем исходный код
COPY . /app/

# Собираем статические файлы
RUN python manage.py collectstatic --noinput

# Выполняем миграции, создаем ботов, добавляем CRON задачи и запускаем приложение
CMD ["bash", "-c", "python manage.py migrate && python manage.py create_bots && python manage.py add_cron_job && cron && python manage.py rundramatiq & python manage.py runserver 0.0.0.0:8000"]
