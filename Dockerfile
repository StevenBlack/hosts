# using container digest is recommended https://github.com/opencontainers/image-spec/blob/main/descriptor.md#digests 
# https://cloud.google.com/architecture/using-container-images

FROM python:3@sha256:b7bfea0126f539ba570a01fb595ee84cc4e7dcac971ad83d12c848942fa52cb6

WORKDIR /usr/src
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN git clone --depth 1 https://github.com/StevenBlack/hosts.git
WORKDIR /usr/src/hosts

# Now you launch this with
#  $ docker build ./
#  $ docker run -it (containerid) bash
