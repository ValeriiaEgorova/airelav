FROM python:3.11-slim

RUN pip install --no-cache-dir pandas faker openpyxl

WORKDIR /app

CMD ["python"]
FROM python:3.11-slim

RUN pip install --upgrade pip && \
    pip install --no-cache-dir pandas faker openpyxl lxml

WORKDIR /app

CMD ["python"]