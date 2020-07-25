#!/bin/bash
docker run -v /tmp/app/build:/tmp/app/build  -it test:test python3 updateHostsFile.py --ip 10.0.92.1 --auto -n -s -e fakenews -o build
