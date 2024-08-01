FROM python:3.10-slim

ENV PYTHONUNBUFFERED 1

WORKDIR /workspace

COPY requirements.txt .
RUN pip install -r requirements.txt

RUN apt-get update && apt-get install -y \
    git \
    vim \
    curl \
    wget \
    postgresql-client \
    procps \
    net-tools \
    redis-tools

COPY . .

CMD ["bash"]