FROM python:latest

RUN mkdir -p /app
WORKDIR /app

RUN python -m pip install --upgrade pip

COPY backend_server/requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY backend_server/src/ /app
COPY config.yml /app
