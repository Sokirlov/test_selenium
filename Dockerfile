FROM selenium/standalone-chrome:latest

# Встановлюємо Python
FROM python:3.12-slim

# Встановлюємо потрібні пакети для запуску
RUN apt-get update && apt-get install -y \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Копіюємо файл з вимогами
COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

# Копіюємо проект в контейнер
COPY . /app
WORKDIR /app


# Встановлюємо команди для запуску скрипту
#CMD ["python", "parser.py"]
