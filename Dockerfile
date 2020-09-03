FROM debian:stretch-backports
RUN apt-get update && apt-get install -y python3-lxml dnsmasq python3-requests && rm -rf /var/lib/apt/lists/*
WORKDIR /tmp/app
ARG ADBLOCK_IP

#COPY ./requirements.txt /tmp/app/requirements.txt
#RUN pip3 install -r requirements.txt

COPY ./ /tmp/app
RUN python3 updateHostsFile.py --ip ${ADBLOCK_IP} -a -n -s -e fakenews -e gambling --blacklist blacklist -o /tmp/app -b

EXPOSE 53/udp
ENTRYPOINT ["/usr/sbin/dnsmasq", "--no-daemon", "--addn-hosts=/tmp/app/hosts"]

