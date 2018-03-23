#!/bin/bash

echo "Running unittests..."
source activate hosts

python testUpdateHostsFile.py
