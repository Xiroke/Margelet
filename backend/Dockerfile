FROM python:3.10-slim

# Устанавливаем рабочую директорию
WORKDIR /app/backend

# Устанавливаем зависимости для сборки (например, gcc для некоторых Python-библиотек)
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Копируем файл зависимостей
COPY requirements.in ./

# Устанавливаем зависимости
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.in

# Копируем приложение
COPY . .

# Указываем порт, который будет слушать приложение
EXPOSE 8080

# Команда запуска
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "4"]