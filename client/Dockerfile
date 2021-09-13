FROM node:16.8.0-alpine

USER root

RUN apk add bash

RUN mkdir /home/node/app
WORKDIR home/node/app

ADD package.json .
ADD package-lock.json .
RUN npm install

USER node

COPY --chown=node:node . /home/node/app

EXPOSE 1234
