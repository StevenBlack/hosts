FROM python:3

WORKDIR /usr/src
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN git clone --depth 1 https://github.com/StevenBlack/hosts.git

# Now you launch this with
#  $ docker build ./
#  $ docker run -it (containerid) bash