# Используем легкую версию Python
FROM python:3.11-slim

# Устанавливаем только необходимые библиотеки внутри контейнера
RUN pip install --no-cache-dir pandas faker openpyxl

# Создаем папку для работы
WORKDIR /app

# Команда по умолчанию (будет заменена при запуске)
CMD ["python"]
# Используем легкую версию Python
FROM python:3.11-slim

# Обновляем pip и устанавливаем зависимости для Excel работы
RUN pip install --upgrade pip && \
    pip install --no-cache-dir pandas faker openpyxl lxml

# Создаем папку для работы
WORKDIR /app

# Команда по умолчанию (будет заменена при запуске)
CMD ["python"]