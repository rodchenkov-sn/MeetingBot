FROM python:latest

RUN mkdir -p /app
WORKDIR /app

RUN python -m pip install --upgrade pip

COPY test/tg_server_adapter/requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY test/tg_server_adapter/src/ /app
