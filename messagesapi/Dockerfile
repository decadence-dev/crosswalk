FROM python:3.8.8-alpine

USER root

RUN apk add --no-cache --virtual .build-deps gcc musl-dev libffi-dev \
    openssl-dev make rust cargo g++
RUN apk add bash

RUN pip install --upgrade pip
RUN pip install poetry

RUN addgroup -g 1000 -S python && adduser -u 1000 -S python -G python
USER python

RUN mkdir home/python/messagesapi
WORKDIR home/python/messagesapi

ADD pyproject.toml .
RUN poetry install

USER root
RUN apk del --no-cache .build-deps

USER python
COPY --chown=python:python . /home/python/messagesapi

EXPOSE 8000
