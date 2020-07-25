FROM arm32v7/debian:stretch-backports
RUN apt-get update && apt-get install -y python3-lxml && rm -rf /var/lib/apt/lists/*

WORKDIR /tmp/app
#COPY ./requirements.txt /tmp/app/requirements.txt
#RUN pip3 install -r requirements.txt

COPY ./ /tmp/app

