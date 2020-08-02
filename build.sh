#!/bin/bash
docker build -t hosts:builder -f Dockerfile .
docker run -v $PWD/build:/tmp/app/build  -it hosts:builder python3 updateHostsFile.py --ip 10.0.92.1 -a -n -s -e fakenews -o build 

echo switching to remote peer
eval $(docker-machine env bananapi)
docker build -t dnsmasq:latest -f dnsmasqDockerfile .
docker stop dnsmasq 
docker rm dnsmasq
docker run --name dnsmasq --network host --dns 1.1.1.1 --restart always -d dnsmasq:latest
