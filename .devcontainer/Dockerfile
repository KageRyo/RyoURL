FROM python:3.10-slim

WORKDIR /workspace

COPY requirements.txt .
RUN pip install -r requirements.txt

RUN apt-get update && apt-get install -y \
    git \
    vim \
    curl \
    wget

COPY . .

CMD ["bash"]