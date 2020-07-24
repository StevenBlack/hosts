FROM arm32v7/python:3.5-stretch
RUN apt-get update && apt-get install -y dnsmasq && rm -rf /var/lib/apt/lists/*

WORKDIR /tmp/app
COPY ./requirements.txt /tmp/app/requirements.txt
RUN pip3 install -r requirements.txt

COPY ./ /tmp/app
ARG dnsproxy_ip
RUN python3 updateHostsFile.py --ip $dnsproxy_ip --auto -n -s -e fakenews

EXPOSE 53/udp
ENTRYPOINT ["/usr/sbin/dnsmasq", "--no-daemon", "--addn-hosts=/tmp/hosts-master/hosts"]
