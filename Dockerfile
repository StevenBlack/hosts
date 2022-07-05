FROM docker.io/python:3-alpine

ENV IN_CONTAINER 1

RUN apk add --no-cache git sudo

COPY . /usr/src/hosts

RUN pip install --no-cache-dir --upgrade -r /usr/src/hosts/requirements.txt

ENV PATH $PATH:/usr/src/hosts
