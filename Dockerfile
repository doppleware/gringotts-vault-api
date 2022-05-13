# Pull base image
FROM python:3.8.13-buster as builder

# Set environment variables
COPY ./gringotts/requirements.txt requirements.txt

# Install pipenv
RUN set -ex && pip install --upgrade pip

# Install dependencies
RUN set -ex && pip install -r requirements.txt

FROM builder as final
WORKDIR /app
COPY ./gringotts/ /app/
COPY ./tests/ /app/
COPY .env /app/

RUN set -ex && bash -c "eval $(grep 'PYTHONDONTWRITEBYTECODE' .env)"
RUN set -ex && bash -c "eval $(grep 'PYTHONUNBUFFERED' .env)"
