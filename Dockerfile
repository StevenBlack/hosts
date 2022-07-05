FROM docker.io/python:3-alpine

ENV IN_CONTAINER 1

RUN apk add --no-cache git sudo

COPY . /hosts

RUN pip install --no-cache-dir --upgrade -r /hosts/requirements.txt

ENV PATH $PATH:/hosts

WORKDIR /hosts
