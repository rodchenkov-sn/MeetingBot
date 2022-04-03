FROM python:latest

RUN mkdir -p /app
WORKDIR /app

RUN python -m pip install --upgrade pip

COPY test/mock_file_service/requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY test/mock_file_service/src/ /app
