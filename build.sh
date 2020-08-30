#!/bin/bash

ADBLOCK_IP=${DOCKER_ADBLOCK_IP:-"0.0.0.0"}
echo "Using DOCKER_ADBLOCK_IP ${ADBLOCK_IP}"

echo "* Building container, with source-code generated above"
docker build --build-arg "ADBLOCK_IP=$ADBLOCK_IP" -t dnsmasq:latest -f Dockerfile .

echo "* Deploying new container"
docker stop dnsmasq 
docker rm dnsmasq
docker run --name dnsmasq --network host --dns 1.1.1.1 --restart always -d dnsmasq:latest
