FROM python:latest

RUN mkdir -p /app
WORKDIR /app

RUN python -m pip install --upgrade pip

COPY test/integration_tests_adapter/requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY test/integration_tests_adapter/src/ /app
