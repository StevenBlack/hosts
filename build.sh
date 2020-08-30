#!/bin/bash

echo "Fetching source"
git pull origin master

echo "Building build-context"
docker build -t hosts:builder -f Dockerfile .
docker run -v $PWD/build:/tmp/app/build  -it hosts:builder python3 updateHostsFile.py --ip $(dig mjay.engineering +short) -a -n -s -e fakenews -e gambling -o build -b

echo "Building container, with source-code generated above"
docker build -t dnsmasq:latest -f dnsmasqDockerfile .
docker stop dnsmasq 
docker rm dnsmasq
docker run --name dnsmasq --network host --dns 1.1.1.1 --restart always -d dnsmasq:latest

sudo chown -R gandalf:users .

docker image prune -af
