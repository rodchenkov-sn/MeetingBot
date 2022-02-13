FROM python:latest

RUN mkdir -p /app
WORKDIR /app

RUN python -m pip install --upgrade pip

COPY calendar_service/requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY calendar_service/src/ /app
COPY config.yml /app