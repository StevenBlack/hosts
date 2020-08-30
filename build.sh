#!/bin/bash

echo "Using DOCKER_ADBLOCK_IP ${DOCKER_ADBLOCK_IP}"
echo "* Building build-context, to use"
docker build -t hosts:builder -f Dockerfile .
docker run -v $PWD:/tmp/app  hosts:builder python3 updateHostsFile.py --ip ${DOCKER_ADBLOCK_IP} -a -n -s -e fakenews -e gambling --blacklist blacklist -o build -b

echo "* Building container, with source-code generated above"
docker build -t dnsmasq:latest -f dnsmasqDockerfile .

echo "* Deploying new container"
docker stop dnsmasq 
docker rm dnsmasq
docker run --name dnsmasq --network host --dns 1.1.1.1 --restart always -d dnsmasq:latest
