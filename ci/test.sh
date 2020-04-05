#!/bin/bash

set -e

echo "Running unit tests..."
source activate hosts

python testUpdateHostsFile.py
