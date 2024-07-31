FROM python:3.10-slim

WORKDIR /workspace

COPY requirements.txt .
RUN pip install -r requirements.txt

RUN apt-get update && apt-get install -y \
    git \
    vim \
    curl \
    wget \
    redis-server

COPY . .

CMD service redis-server start && python manage.py runserver 0.0.0.0:8000